const BASE_URL = "http://127.0.0.1:8000";



document.getElementById("submitBtn").addEventListener("click", async () => {
  const username = document.getElementById("username").value;
  const email = document.getElementById("email").value;
  const message = document.getElementById("message").value;

  const res = await fetch(`${BASE_URL}/support/request`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, message })
  });

  const data = await res.json();
  document.getElementById("result").innerText =
    `Ticket #${data.ticket_id} created.`;
});