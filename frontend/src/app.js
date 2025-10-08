const form = document.getElementById('transaction-form');
const resultDiv = document.getElementById('result');

form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const formData = new FormData(form);
    const data = {
        plan_id: 'prod_oVJG1FuPA2Nix',
        checkout_link: 'plan_oPKqUgfiFWUVO',
        amount: 5,
    };

    try {
        const response = await fetch('http://localhost:8000/api/transaction', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const result = await response.json();
        resultDiv.innerHTML = `<p>Transaction successful! ID: ${result.id}</p>`;
    } catch (error) {
        resultDiv.innerHTML = `<p>Error: ${error.message}</p>`;
    }
});