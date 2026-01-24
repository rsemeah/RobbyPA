// Calculator App Logic
let currentDisplay = '0';
let previousValue = null;
let operator = null;
let shouldResetDisplay = false;

function updateDisplay() {
    document.getElementById('display').textContent = currentDisplay;
}

function clearDisplay() {
    currentDisplay = '0';
    previousValue = null;
    operator = null;
    shouldResetDisplay = false;
    updateDisplay();
}

function backspace() {
    if (currentDisplay.length > 1) {
        currentDisplay = currentDisplay.slice(0, -1);
    } else {
        currentDisplay = '0';
    }
    updateDisplay();
}

function appendNumber(num) {
    if (shouldResetDisplay) {
        currentDisplay = num;
        shouldResetDisplay = false;
    } else {
        if (currentDisplay === '0' && num !== '.') {
            currentDisplay = num;
        } else if (num === '.' && currentDisplay.includes('.')) {
            return;
        } else {
            currentDisplay += num;
        }
    }
    updateDisplay();
}

function appendOperator(op) {
    if (operator !== null && !shouldResetDisplay) {
        calculate();
    }

    previousValue = parseFloat(currentDisplay);
    operator = op;
    shouldResetDisplay = true;
}

function calculate() {
    if (operator === null || previousValue === null) {
        return;
    }

    const current = parseFloat(currentDisplay);
    let result;

    switch (operator) {
        case '+':
            result = previousValue + current;
            break;
        case '-':
            result = previousValue - current;
            break;
        case '*':
            result = previousValue * current;
            break;
        case '/':
            if (current === 0) {
                alert('Cannot divide by zero!');
                clearDisplay();
                return;
            }
            result = previousValue / current;
            break;
        default:
            return;
    }

    currentDisplay = result.toString();
    operator = null;
    previousValue = null;
    shouldResetDisplay = true;
    updateDisplay();
}

// Keyboard support
document.addEventListener('keydown', (e) => {
    if (e.key >= '0' && e.key <= '9' || e.key === '.') {
        appendNumber(e.key);
    } else if (e.key === '+' || e.key === '-' || e.key === '*' || e.key === '/') {
        appendOperator(e.key);
    } else if (e.key === 'Enter' || e.key === '=') {
        calculate();
    } else if (e.key === 'Backspace') {
        backspace();
    } else if (e.key === 'Escape') {
        clearDisplay();
    }
});

updateDisplay();