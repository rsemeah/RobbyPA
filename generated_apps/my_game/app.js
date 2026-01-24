// Simple Game Logic
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Game state
let gameRunning = true;
let score = 0;
let highScore = parseInt(localStorage.getItem('highScore')) || 0;

// Player
const player = {
    x: canvas.width / 2,
    y: canvas.height / 2,
    size: 30,
    speed: 5,
    color: '#4CAF50'
};

// Stars (collectibles)
let stars = [];

// Obstacles
let obstacles = [];

// Input handling
const keys = {};
document.addEventListener('keydown', (e) => {
    keys[e.key.toLowerCase()] = true;
});
document.addEventListener('keyup', (e) => {
    keys[e.key.toLowerCase()] = false;
});

// Create star
function createStar() {
    return {
        x: Math.random() * (canvas.width - 30) + 15,
        y: Math.random() * (canvas.height - 30) + 15,
        size: 20,
        collected: false
    };
}

// Create obstacle
function createObstacle() {
    return {
        x: Math.random() * (canvas.width - 30) + 15,
        y: Math.random() * (canvas.height - 30) + 15,
        size: 25,
        speedX: (Math.random() - 0.5) * 3,
        speedY: (Math.random() - 0.5) * 3
    };
}

// Initialize game objects
function initGame() {
    stars = [];
    obstacles = [];

    for (let i = 0; i < 5; i++) {
        stars.push(createStar());
    }

    for (let i = 0; i < 3; i++) {
        obstacles.push(createObstacle());
    }
}

// Update player position
function updatePlayer() {
    if (keys['arrowup'] || keys['w']) {
        player.y = Math.max(player.size / 2, player.y - player.speed);
    }
    if (keys['arrowdown'] || keys['s']) {
        player.y = Math.min(canvas.height - player.size / 2, player.y + player.speed);
    }
    if (keys['arrowleft'] || keys['a']) {
        player.x = Math.max(player.size / 2, player.x - player.speed);
    }
    if (keys['arrowright'] || keys['d']) {
        player.x = Math.min(canvas.width - player.size / 2, player.x + player.speed);
    }
}

// Update obstacles
function updateObstacles() {
    obstacles.forEach(obstacle => {
        obstacle.x += obstacle.speedX;
        obstacle.y += obstacle.speedY;

        // Bounce off walls
        if (obstacle.x <= 0 || obstacle.x >= canvas.width) {
            obstacle.speedX *= -1;
        }
        if (obstacle.y <= 0 || obstacle.y >= canvas.height) {
            obstacle.speedY *= -1;
        }
    });
}

// Check collisions
function checkCollisions() {
    // Check star collisions
    stars.forEach(star => {
        if (!star.collected) {
            const dx = player.x - star.x;
            const dy = player.y - star.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < (player.size / 2 + star.size / 2)) {
                star.collected = true;
                score += 10;
                document.getElementById('score').textContent = score;
                stars.push(createStar());
            }
        }
    });

    // Check obstacle collisions
    obstacles.forEach(obstacle => {
        const dx = player.x - obstacle.x;
        const dy = player.y - obstacle.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < (player.size / 2 + obstacle.size / 2)) {
            endGame();
        }
    });
}

// Draw everything
function draw() {
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw player
    ctx.fillStyle = player.color;
    ctx.beginPath();
    ctx.arc(player.x, player.y, player.size / 2, 0, Math.PI * 2);
    ctx.fill();

    // Draw stars
    stars.forEach(star => {
        if (!star.collected) {
            ctx.font = `${star.size}px Arial`;
            ctx.fillText('⭐', star.x - star.size / 2, star.y + star.size / 2);
        }
    });

    // Draw obstacles
    obstacles.forEach(obstacle => {
        ctx.font = `${obstacle.size}px Arial`;
        ctx.fillText('🔴', obstacle.x - obstacle.size / 2, obstacle.y + obstacle.size / 2);
    });
}

// Game loop
function gameLoop() {
    if (!gameRunning) return;

    updatePlayer();
    updateObstacles();
    checkCollisions();
    draw();

    requestAnimationFrame(gameLoop);
}

// End game
function endGame() {
    gameRunning = false;

    if (score > highScore) {
        highScore = score;
        localStorage.setItem('highScore', highScore);
        document.getElementById('highScore').textContent = highScore;
    }

    document.getElementById('finalScore').textContent = score;
    document.getElementById('gameOver').classList.remove('hidden');
}

// Restart game
function restartGame() {
    gameRunning = true;
    score = 0;
    document.getElementById('score').textContent = score;
    player.x = canvas.width / 2;
    player.y = canvas.height / 2;

    initGame();
    document.getElementById('gameOver').classList.add('hidden');
    gameLoop();
}

document.getElementById('restartBtn').addEventListener('click', restartGame);
document.getElementById('highScore').textContent = highScore;

// Start game
initGame();
gameLoop();