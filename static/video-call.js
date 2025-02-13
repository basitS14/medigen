// static/js/video-call.js
let client = null;
let localStream = null;
let remoteStream = null;

async function initializeCall() {
    // Initialize Agora client
    client = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' });
    
    try {
        // Fetch token from your server
        const response = await fetch(`/get-agora-token/?channel=${appointment.channelName}`);
        const data = await response.json();
        
        // Join the channel
        await client.join(data.appId, appointment.channelName, data.token, null);
        
        // Create local stream
        localStream = AgoraRTC.createStream({
            audio: true,
            video: true
        });
        
        // Initialize local stream
        await localStream.init();
        
        // Play local stream
        localStream.play('local-video');
        
        // Publish local stream
        await client.publish(localStream);
        
        // Subscribe to remote streams
        client.on('stream-added', async (evt) => {
            const stream = evt.stream;
            await client.subscribe(stream);
            stream.play('remote-video');
            remoteStream = stream;
        });
        
    } catch (error) {
        console.error('Error initializing call:', error);
    }
}

// Handle controls
document.getElementById('muteAudio').onclick = () => {
    if (localStream.audio) {
        localStream.muteAudio();
        document.getElementById('muteAudio').textContent = 'Unmute Audio';
    } else {
        localStream.unmuteAudio();
        document.getElementById('muteAudio').textContent = 'Mute Audio';
    }
};

document.getElementById('muteVideo').onclick = () => {
    if (localStream.video) {
        localStream.muteVideo();
        document.getElementById('muteVideo').textContent = 'Show Video';
    } else {
        localStream.unmuteVideo();
        document.getElementById('muteVideo').textContent = 'Hide Video';
    }
};

document.getElementById('endCall').onclick = async () => {
    if (localStream) {
        localStream.close();
    }
    if (client) {
        await client.leave();
    }
    window.location.href = '/profile/'; // Redirect to profile page
};

// Initialize call when page loads
initializeCall();