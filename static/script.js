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

// Đăng ký Service Worker
if ("serviceWorker" in navigator) {

    window.addEventListener("load", () => {

        navigator.serviceWorker.register("/service-worker.js")
            .then(() => console.log("Service Worker registered"))
            .catch(err => console.log(err));

    });

}