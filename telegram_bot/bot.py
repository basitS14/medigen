import os
import logging
import django
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, 
    CallbackQueryHandler, ConversationHandler, ContextTypes
)
from django.conf import settings
from django.db.models import Q
from meds.models import Doctors, Appointment, Availability, OnlineAvailability, OnlineAvailabilityPartime, CustomUser
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define conversation states
(
    START, BOOKING_OPTION, DOCTOR_SELECTION, SEARCH_DOCTOR,
    APPOINTMENT_MODE, DATE_SELECTION, TIME_SELECTION, CONFIRMATION,
    PATIENT_INFO
) = range(9)

# Helper function to get available dates for a doctor based on availability
def get_available_dates(doctor, mode='offline'):
    today = datetime.date.today()
    available_dates = []
    
    # Get the doctor's availability based on mode
    if mode == 'offline':
        availabilities = Availability.objects.filter(doctor=doctor)
    elif mode == 'online':
        availabilities = list(OnlineAvailability.objects.filter(doctor=doctor))
        availabilities.extend(list(OnlineAvailabilityPartime.objects.filter(doctor=doctor)))
    
    # Map day names to weekday numbers
    day_mapping = {
        'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
        'Friday': 4, 'Saturday': 5, 'Sunday': 6
    }
    
    # Create a set of days the doctor is available
    available_days = set()
    for avail in availabilities:
        if avail.day_of_week in day_mapping:
            available_days.add(day_mapping[avail.day_of_week])
    
    # Find the next 10 available dates
    current_date = today
    count = 0
    while count < 10:
        weekday = current_date.weekday()
        if weekday in available_days:
            available_dates.append(current_date)
            count += 1
        current_date += datetime.timedelta(days=1)
        
        # Safety limit - don't check more than 30 days ahead
        if (current_date - today).days > 30:
            break
    
    return available_dates

# Helper function to get available time slots for a doctor on a specific date
def get_available_time_slots(doctor, date, mode='offline'):
    # Convert string date to datetime object if needed
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    
    # Get day of week
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_of_week = day_names[date.weekday()]
    
    # Get the doctor's availability for this day
    if mode == 'offline':
        availabilities = Availability.objects.filter(doctor=doctor, day_of_week=day_of_week)
    elif mode == 'online':
        availabilities = list(OnlineAvailability.objects.filter(doctor=doctor, day_of_week=day_of_week))
        availabilities.extend(list(OnlineAvailabilityPartime.objects.filter(doctor=doctor, day_of_week=day_of_week)))
    
    # If no availabilities found, return empty list
    if not availabilities:
        return []
    
    # Get existing appointments for this doctor on this date
    existing_appointments = Appointment.objects.filter(
        doctor=doctor, date=date, appointment_mode=mode
    )
    
    # Create time slots in 30-minute increments
    available_slots = []
    for availability in availabilities:
        current_time = availability.available_from
        end_time = availability.available_to
        
        # If this availability has a break, handle it
        has_break = False
        break_start = None
        break_end = None
        
        if hasattr(availability, 'break_from') and hasattr(availability, 'break_to'):
            if availability.break_from and availability.break_to:
                has_break = True
                break_start = availability.break_from
                break_end = availability.break_to
        
        while current_time < end_time:
            # Create end time for this slot (30 minutes later)
            slot_end = (datetime.datetime.combine(date, current_time) + 
                        datetime.timedelta(minutes=30)).time()
            
            # Skip if this slot is during break time
            if has_break and (current_time >= break_start and current_time < break_end):
                current_time = slot_end
                continue
            
            # Check if this slot conflicts with existing appointments
            slot_available = True
            for appt in existing_appointments:
                if (current_time < appt.end_time and slot_end > appt.start_time):
                    slot_available = False
                    break
            
            # Add slot if available
            if slot_available:
                # Format for display
                slot_str = f"{current_time.strftime('%H:%M')} - {slot_end.strftime('%H:%M')}"
                # Store actual times for database
                available_slots.append({
                    'display': slot_str,
                    'start': current_time,
                    'end': slot_end
                })
            
            # Move to next slot
            current_time = slot_end
            
            # Check number of slots against max_appointments
            if len(available_slots) >= availability.max_appointments:
                break
    
    return available_slots

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the conversation and ask if user wants to book an appointment."""
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("Book an appointment", callback_data='book')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Hello {user.first_name}! I'm your appointment booking assistant. "
        f"Would you like to book a doctor's appointment?",
        reply_markup=reply_markup
    )
    
    return BOOKING_OPTION

async def booking_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user's choice for booking."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("Search by name", callback_data='search'),
            InlineKeyboardButton("View all doctors", callback_data='list')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text="How would you like to find a doctor?",
        reply_markup=reply_markup
    )
    
    return DOCTOR_SELECTION

async def doctor_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle doctor selection method."""
    query = update.callback_query
    await query.answer()
    
    choice = query.data
    
    if choice == 'search':
        await query.edit_message_text(
            text="Please enter the doctor's name you're looking for:"
        )
        return SEARCH_DOCTOR
    
    elif choice == 'list':
        # Fetch all doctors from database
        doctors = Doctors.objects.all()
        
        if not doctors:
            await query.edit_message_text(
                text="No doctors are currently available in our system."
            )
            return ConversationHandler.END
        
        keyboard = []
        for i, doctor in enumerate(doctors[:10], 1):  # Limit to 10 doctors for better UI
            # Store doctor ID in context.user_data for later use
            context.user_data[f"doctor_{i}"] = doctor.id
            keyboard.append([InlineKeyboardButton(
                f"{i}. Dr. {doctor.user.full_name} - {doctor.specialization}",
                callback_data=f"doctor_{i}"
            )])
        
        keyboard.append([InlineKeyboardButton("Cancel", callback_data='cancel')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text="Please select a doctor:",
            reply_markup=reply_markup
        )
        
        return APPOINTMENT_MODE

async def search_doctor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle search for doctors."""
    search_term = update.message.text
    
    # Search for doctors by name
    doctors = Doctors.objects.filter(
        Q(user__full_name__icontains=search_term) | 
        Q(specialization__icontains=search_term)
    )[:5]  # Limit to top 5 matches
    
    if not doctors:
        await update.message.reply_text(
            "No doctors found matching your search. Please try another name or view all doctors.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("View all doctors", callback_data='list')],
                [InlineKeyboardButton("Search again", callback_data='search')],
                [InlineKeyboardButton("Cancel", callback_data='cancel')]
            ])
        )
        return DOCTOR_SELECTION
    
    keyboard = []
    for i, doctor in enumerate(doctors, 1):
        # Store doctor ID in context.user_data for later use
        context.user_data[f"doctor_{i}"] = doctor.id
        keyboard.append([InlineKeyboardButton(
            f"{i}. Dr. {doctor.user.full_name} - {doctor.specialization}",
            callback_data=f"doctor_{i}"
        )])
    
    keyboard.append([InlineKeyboardButton("Cancel", callback_data='cancel')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text="Here are the doctors matching your search. Please select one:",
        reply_markup=reply_markup
    )
    
    return APPOINTMENT_MODE

async def appointment_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle appointment mode selection."""
    query = update.callback_query
    await query.answer()
    
    choice = query.data
    
    if choice.startswith('doctor_'):
        doctor_index = choice.split('_')[1]
        doctor_id = context.user_data.get(f"doctor_{doctor_index}")
        
        if not doctor_id:
            await query.edit_message_text("Error: Doctor not found. Please try again.")
            return ConversationHandler.END
        
        # Store selected doctor ID in context
        context.user_data['selected_doctor_id'] = doctor_id
        
        # Get doctor details
        doctor = Doctors.objects.get(id=doctor_id)
        context.user_data['doctor_name'] = f"Dr. {doctor.user.full_name}"
        
        # Ask for appointment mode
        keyboard = [
            [
                InlineKeyboardButton("Online", callback_data='online'),
                InlineKeyboardButton("Offline", callback_data='offline')
            ],
            [InlineKeyboardButton("Cancel", callback_data='cancel')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=f"You've selected {context.user_data['doctor_name']}. "
                 f"Would you like an online or offline appointment?",
            reply_markup=reply_markup
        )
        
        return DATE_SELECTION
    
    elif choice == 'cancel':
        await query.edit_message_text("Booking cancelled. Type /start to begin again.")
        return ConversationHandler.END

async def date_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle date selection."""
    query = update.callback_query
    await query.answer()
    
    choice = query.data
    
    if choice in ['online', 'offline']:
        # Store appointment mode
        context.user_data['appointment_mode'] = choice
        
        # Get doctor object
        doctor_id = context.user_data['selected_doctor_id']
        doctor = Doctors.objects.get(id=doctor_id)
        
        # Get available dates
        available_dates = get_available_dates(doctor, mode=choice)
        
        if not available_dates:
            await query.edit_message_text(
                f"No available dates found for {context.user_data['doctor_name']} "
                f"for {choice} appointments. Please try another doctor."
            )
            return ConversationHandler.END
        
        keyboard = []
        for i, date in enumerate(available_dates):
            date_str = date.strftime('%Y-%m-%d')
            display_date = date.strftime('%A, %B %d, %Y')
            context.user_data[f'date_{i}'] = date_str
            keyboard.append([InlineKeyboardButton(display_date, callback_data=f'date_{i}')])
        
        keyboard.append([InlineKeyboardButton("Cancel", callback_data='cancel')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=f"Please select a date for your {choice} appointment:",
            reply_markup=reply_markup
        )
        
        return TIME_SELECTION
    
    elif choice == 'cancel':
        await query.edit_message_text("Booking cancelled. Type /start to begin again.")
        return ConversationHandler.END

async def time_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle time slot selection."""
    query = update.callback_query
    await query.answer()
    
    choice = query.data
    
    if choice.startswith('date_'):
        date_index = choice.split('_')[1]
        selected_date_str = context.user_data.get(f'date_{date_index}')
        
        if not selected_date_str:
            await query.edit_message_text("Error: Date not found. Please try again.")
            return ConversationHandler.END
        
        # Store selected date
        context.user_data['selected_date'] = selected_date_str
        selected_date = datetime.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        
        # Get doctor object
        doctor_id = context.user_data['selected_doctor_id']
        doctor = Doctors.objects.get(id=doctor_id)
        
        # Get available time slots
        mode = context.user_data['appointment_mode']
        available_slots = get_available_time_slots(doctor, selected_date, mode=mode)
        
        if not available_slots:
            await query.edit_message_text(
                f"No available time slots found for {context.user_data['doctor_name']} "
                f"on {selected_date.strftime('%A, %B %d, %Y')}. Please try another date."
            )
            keyboard = [[InlineKeyboardButton("Go back to date selection", callback_data=context.user_data['appointment_mode'])]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text="No available slots. Try another date?",
                reply_markup=reply_markup
            )
            return DATE_SELECTION
        
        keyboard = []
        for i, slot in enumerate(available_slots):
            context.user_data[f'slot_{i}'] = {
                'start': slot['start'].strftime('%H:%M'),
                'end': slot['end'].strftime('%H:%M')
            }
            keyboard.append([InlineKeyboardButton(slot['display'], callback_data=f'slot_{i}')])
        
        keyboard.append([InlineKeyboardButton("Cancel", callback_data='cancel')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=f"Please select a time slot for your appointment on "
                 f"{selected_date.strftime('%A, %B %d, %Y')}:",
            reply_markup=reply_markup
        )
        
        return PATIENT_INFO
    
    elif choice == 'cancel':
        await query.edit_message_text("Booking cancelled. Type /start to begin again.")
        return ConversationHandler.END

async def patient_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle patient information collection."""
    query = update.callback_query
    await query.answer()
    
    choice = query.data
    
    if choice.startswith('slot_'):
        slot_index = choice.split('_')[1]
        selected_slot = context.user_data.get(f'slot_{slot_index}')
        
        if not selected_slot:
            await query.edit_message_text("Error: Time slot not found. Please try again.")
            return ConversationHandler.END
        
        # Store selected slot
        context.user_data['selected_slot'] = selected_slot
        
        await query.edit_message_text(
            "Please enter the patient's full name:"
        )
        
        return CONFIRMATION
    
    elif choice == 'cancel':
        await query.edit_message_text("Booking cancelled. Type /start to begin again.")
        return ConversationHandler.END

async def confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle booking confirmation."""
    patient_name = update.message.text
    context.user_data['patient_name'] = patient_name
    
    # Get all the booking details
    doctor_id = context.user_data['selected_doctor_id']
    date_str = context.user_data['selected_date']
    slot = context.user_data['selected_slot']
    mode = context.user_data['appointment_mode']
    
    # Format for confirmation message
    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    formatted_date = date_obj.strftime('%A, %B %d, %Y')
    
    # Create confirmation message
    confirmation_text = (
        f"Please confirm your appointment:\n\n"
        f"Doctor: {context.user_data['doctor_name']}\n"
        f"Patient: {patient_name}\n"
        f"Date: {formatted_date}\n"
        f"Time: {slot['start']} - {slot['end']}\n"
        f"Mode: {mode.capitalize()}\n\n"
        f"Would you like to confirm this booking?"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("Confirm", callback_data='confirm'),
            InlineKeyboardButton("Cancel", callback_data='cancel')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text=confirmation_text,
        reply_markup=reply_markup
    )
    
    return ConversationHandler.END

async def save_appointment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save the appointment to the database."""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'confirm':
        try:
            # Get all the booking details
            doctor_id = context.user_data['selected_doctor_id']
            date_str = context.user_data['selected_date']
            slot = context.user_data['selected_slot']
            mode = context.user_data['appointment_mode']
            patient_name = context.user_data['patient_name']
            
            # Get objects from database
            doctor = Doctors.objects.get(id=doctor_id)
            
            # Create a dummy user as the appointment booker
            # In a real app, you'd want to link this to the Telegram user
            # or have them log in through your Django app
            try:
                user = CustomUser.objects.get(email="telegram_user@example.com")
            except CustomUser.DoesNotExist:
                # Create a dummy user for Telegram bookings
                from django.contrib.auth.models import User
                user = CustomUser.objects.create(
                    email="telegram_user@example.com",
                    phone="0000000000",
                    full_name="Telegram User"
                )
            
            # Parse date and times
            appointment_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time = datetime.datetime.strptime(slot['start'], '%H:%M').time()
            end_time = datetime.datetime.strptime(slot['end'], '%H:%M').time()
            
            # Create appointment
            appointment = Appointment.objects.create(
                doctor=doctor,
                username=user,
                patient=patient_name,
                date=appointment_date,
                start_time=start_time,
                end_time=end_time,
                notes=f"Booked via Telegram Bot",
                appointment_mode=mode,
                created_at=datetime.datetime.now()
            )
            
            await query.edit_message_text(
                f"Appointment confirmed! Your appointment with {context.user_data['doctor_name']} "
                f"is scheduled for {appointment_date.strftime('%A, %B %d, %Y')} "
                f"at {slot['start']}. Please arrive 10 minutes early."
            )
            
        except Exception as e:
            logger.error(f"Error saving appointment: {e}")
            await query.edit_message_text(
                "There was an error booking your appointment. Please try again later."
            )
    
    elif query.data == 'cancel':
        await query.edit_message_text("Booking cancelled. Type /start to begin again.")
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel and end the conversation."""
    await update.message.reply_text("Booking cancelled. Type /start to begin again.")
    return ConversationHandler.END

def create_telegram_bot():
    """Create and return the Telegram application."""
    # Initialize the bot with your token - replace with your actual bot token
    token = os.environ.get('TELEGRAM_BOT_TOKEN', '8101548298:AAGINtAwPcvjlniau7KTbZBHccLAkRMh-bc')
    application = Application.builder().token(token).build()
    
    # Define conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            BOOKING_OPTION: [CallbackQueryHandler(booking_option)],
            DOCTOR_SELECTION: [
                CallbackQueryHandler(doctor_selection),
                MessageHandler(filters.TEXT & ~filters.COMMAND, search_doctor)
            ],
            SEARCH_DOCTOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_doctor)],
            APPOINTMENT_MODE: [CallbackQueryHandler(appointment_mode)],
            DATE_SELECTION: [CallbackQueryHandler(date_selection)],
            TIME_SELECTION: [CallbackQueryHandler(time_selection)],
            PATIENT_INFO: [CallbackQueryHandler(patient_info)],
            CONFIRMATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, confirmation),
                CallbackQueryHandler(save_appointment)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(conv_handler)
    
    # Add error handler
    application.add_error_handler(lambda update, context: logger.error(f"Error: {context.error}"))
    
    return application

# Function to start the bot
def start_bot():
    """Start the Telegram bot."""
    try:
        # Initialize Django (if not already done)
        if not settings.configured:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
            django.setup()
        
        application = create_telegram_bot()
        
        # Start the bot in a separate thread
        application.run_polling(drop_pending_updates=True)
        
        logger.info("Telegram bot started successfully!")
        
    except Exception as e:
        logger.error(f"Failed to start Telegram bot: {e}")

bot_application = None

def get_bot_application():
    """Get or create the bot application."""
    global bot_application
    if bot_application is None:
        bot_application = create_telegram_bot()
    return bot_application