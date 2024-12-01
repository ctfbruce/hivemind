const feed = document.getElementById('live-feed');

// Simulate receiving a new post (this would typically come from a WebSocket)
function addNewPost(content, timestamp) {
    const newItem = document.createElement('div');
    newItem.classList.add('live-feed-item');

    // Add content and timestamp
    newItem.innerHTML = `
        <p class="post-text">${content}</p>
        <span class="post-time">${timestamp}</span>
    `;

    // Prepend the new item to the feed
    feed.prepend(newItem);

    // Optional: Scroll to top to show the new item
    feed.scrollTop = 0;
}


