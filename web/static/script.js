document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;

    // Theme Toggle Logic
    themeToggle.addEventListener('click', () => {
        const currentTheme = htmlElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        htmlElement.setAttribute('data-theme', newTheme);
    });

    // Fetch Stock Data
    fetchStocks();

    // Auto-update every 2 seconds
    setInterval(fetchStocks, 2000);

    async function fetchStocks() {
        try {
            const response = await fetch('/api/stocks');
            const data = await response.json();


            renderStocks('spain-cards', data.spain);
            renderStocks('usa-cards', data.usa);
        } catch (error) {
            console.error('Error fetching stocks:', error);
        }
    }

    function renderStocks(containerId, stocks) {
        const container = document.getElementById(containerId);

        // Initial load: Create cards if container is empty (or has skeletons)
        if (container.querySelector('.loading-skeleton')) {
            container.innerHTML = '';
        }

        stocks.forEach((stock, index) => {
            const cardId = `stock-${stock.symbol}`;
            let card = document.getElementById(cardId);

            const isPositive = stock.change.includes('+');
            const changeClass = isPositive ? 'positive' : 'negative';
            const icon = isPositive ? '<i class="fa-solid fa-arrow-trend-up"></i>' : '<i class="fa-solid fa-arrow-trend-down"></i>';

            if (!card) {
                // Create new card
                card = document.createElement('div');
                card.id = cardId;
                card.className = 'stock-card';
                card.style.animation = `fadeIn 0.5s ease forwards ${index * 0.1}s`;
                card.style.opacity = '0'; // Start invisible for animation

                card.innerHTML = `
                    <div class="stock-info">
                        <h4>${stock.symbol}</h4>
                        <p>${stock.name}</p>
                    </div>
                    <div class="stock-price">
                        <span class="price" id="price-${stock.symbol}">$${stock.price}</span>
                        <span class="change ${changeClass}" id="change-${stock.symbol}">${icon} ${stock.change}</span>
                    </div>
                `;
                container.appendChild(card);
            } else {
                // Update existing card numbers only
                const priceEl = document.getElementById(`price-${stock.symbol}`);
                const changeEl = document.getElementById(`change-${stock.symbol}`);

                if (priceEl && priceEl.innerText !== `$${stock.price}`) {
                    priceEl.innerText = `$${stock.price}`;
                    priceEl.style.color = isPositive ? 'var(--accent-color)' : '#ff4d4d'; // Flash color
                    setTimeout(() => { priceEl.style.color = ''; }, 500); // Reset color
                }

                if (changeEl) {
                    changeEl.className = `change ${changeClass}`;
                    changeEl.innerHTML = `${icon} ${stock.change}`;
                }
            }
        });
    }
});

// Add keyframe for fade in dynamically
const styleSheet = document.createElement("style");
styleSheet.innerText = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(styleSheet);
