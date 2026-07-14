async function loadWeather() {

    try {

        const response = await fetch("/api/weather");

        const data = await response.json();

        if (data.status === "offline") {

            document.getElementById("warnings").innerHTML =
                "<div class='warning-item'><h4>❌ Mất kết nối</h4><p>Không lấy được dữ liệu thời tiết.</p></div>";

            return;
        }

        const current = data.current;

        document.getElementById("temperature").innerHTML =
            current.temperature + " °C";

        document.getElementById("humidity").innerHTML =
            current.humidity + " %";

        document.getElementById("rain").innerHTML =
            current.rain_probability + " %";

        document.getElementById("cloud").innerHTML =
            current.cloud + " %";

        document.getElementById("uv").innerHTML =
            current.uv;

        document.getElementById("wind").innerHTML =
            current.wind + " km/h";

        document.getElementById("update").innerHTML =
            current.time;

        const warningBox = document.getElementById("warnings");

        warningBox.innerHTML = "";

        if (data.warnings.length === 0) {

            warningBox.innerHTML =
                "<div class='warning-item'><h4>✅ An toàn</h4><p>Hiện chưa có cảnh báo.</p></div>";

        } else {

            data.warnings.forEach(w => {

                warningBox.innerHTML += `
                    <div class="warning-item">
                        <h4>${w.title}</h4>
                        <p>${w.message}</p>
                    </div>
                `;

            });

        }

    } catch (e) {

        console.log(e);

    }

}

// Tải lần đầu
loadWeather();

// Tự động cập nhật mỗi 30 giây
setInterval(loadWeather, 30000);

// ==========================================
// Web Push: đăng ký nhận thông báo trên máy
// ==========================================

function urlBase64ToUint8Array(base64String) {

    const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
    const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
    const rawData = atob(base64);

    return Uint8Array.from([...rawData].map(c => c.charCodeAt(0)));

}

async function subscribeToPush(registration) {

    if (!("PushManager" in window)) {
        console.log("Trình duyệt không hỗ trợ Push");
        return;
    }

    const permission = await Notification.requestPermission();

    if (permission !== "granted") {
        console.log("Người dùng chưa cho phép thông báo");
        return;
    }

    // Nếu đã subscribe từ trước thì dùng lại, không tạo mới
    let subscription = await registration.pushManager.getSubscription();

    if (!subscription) {

        const keyResponse = await fetch("/api/vapid-public-key");
        const keyData = await keyResponse.json();

        subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(keyData.publicKey)
        });

    }

    await fetch("/api/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(subscription)
    });

    console.log("Đã đăng ký nhận cảnh báo thời tiết trên máy này");

}

// Đăng ký Service Worker + subscribe push
if ("serviceWorker" in navigator) {

    window.addEventListener("load", () => {

        navigator.serviceWorker.register("/service-worker.js")
            .then(registration => {

                console.log("Service Worker registered");

                subscribeToPush(registration);

            })
            .catch(err => console.log(err));

    });

}
