document.getElementById('transaction-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const resultDiv = document.getElementById('result');
    resultDiv.textContent = 'Processing...';
    try {
        const res = await fetch('http://127.0.0.1:8000/transactions/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount: 5, plan_id: 'prod_oVJG1FuPA2Nix', checkout_link: 'plan_oPKqUgfiFWUVO' })
        });
        if (!res.ok) throw new Error('Request failed ' + res.status);
        const data = await res.json();
        resultDiv.innerHTML = `<div class="alert alert-success">Transaction successful! ID: ${data.id}</div>`;
    } catch (err) {
        resultDiv.innerHTML = `<div class="alert alert-danger">Error: ${err.message}</div>`;
    }
});
