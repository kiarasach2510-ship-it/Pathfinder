try {
    // This points directly to her Flask server running on your computer
    const response = await fetch('http://127.0.0.1:5000/career-advice', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json' 
        },
        // Wraps your history array in the "messages" object her code expects
        body: JSON.stringify({ messages: messageHistory }) 
    });

    const data = await response.json();
    
    // Her code returns: {"messages": messages} -> we save it over ours
    messageHistory = data.messages;
    
    // Pull the latest text out from the last item in the array
    const latestAssistantMessage = messageHistory[messageHistory.length - 1].content;
    
    appendChatBubble(latestAssistantMessage, 'assistant-bubble');
    chatWindow.scrollTop = chatWindow.scrollHeight;

} catch (err) {
    console.error("Connection error to Flask:", err);
    appendChatBubble("Could not connect to the backend server. Make sure the Python app is running in your VS Code terminal!", 'assistant-bubble');
}

// Example Frontend Fetch Setup
const token = await firebase.auth().currentUser.getIdToken(); // Get token from Firebase

const response = await fetch('http://localhost:5001/career-advice', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}` // This must match your backend's expected format
  },
  body: JSON.stringify({
    messages: [
      { role: "user", content: "Hello!" }
    ]
  })
});

const data = await response.json();
console.log(data);