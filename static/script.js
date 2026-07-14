// ==========================================
// Đổ dữ liệu vào thanh đo (dial mưa + bar cards)
// value/max được giới hạn trong khoảng 0-100%
// ==========================================

function setGauge(el, value, max) {

    if (!el) return;

    const pct = Math.max(0, Math.min(100, (Number(value) / max) * 100));

    el.style.setProperty("--pct", pct);

}

// ==========================================
// Đổi thời gian API sang giờ Việt Nam thật (Open-Meteo trả về giờ UTC)
// ==========================================

function formatVNTime(raw) {

    if (!raw) return "--";

    let iso = raw;

    // Nếu chuỗi không kèm thông tin múi giờ (không có Z hoặc +hh:mm) thì hiểu là giờ UTC
    if (!/[Zz]|[+-]\d{2}:?\d{2}$/.test(iso)) {
        iso += "Z";
    }

    const date = new Date(iso);

    if (isNaN(date.getTime())) return raw;

    return date.toLocaleString("vi-VN", {
        timeZone: "Asia/Ho_Chi_Minh",
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit"
    });

}

// ==========================================
// Đếm số mượt: chạy từ giá trị cũ -> giá trị mới thay vì nhảy khựng
// ==========================================

function animateNumber(id, value, decimals, suffix) {

    const el = document.getElementById(id);

    if (!el) return;

    const target = Number(value);

    if (Number.isNaN(target)) {
        el.textContent = value;
        return;
    }

    const start = parseFloat(el.dataset.raw || "0");
    const t0 = performance.now();
    const duration = 700;

    function tick(now) {

        const t = Math.min(1, (now - t0) / duration);
        const eased = 1 - Math.pow(1 - t, 3);
        const current = start + (target - start) * eased;

        el.textContent = current.toFixed(decimals) + (suffix || "");

        if (t < 1) {
            requestAnimationFrame(tick);
        } else {
            el.dataset.raw = String(target);
        }

    }

    requestAnimationFrame(tick);

}

// ==========================================
// Nền động: mật độ mưa + độ đậm mây theo dữ liệu thật
// ==========================================

function updateRainLayer(probability) {

    const layer = document.getElementById("rainLayer");

    if (!layer) return;

    const desired = Math.round((probability / 100) * 40);

    if (layer.dataset.count !== String(desired)) {

        layer.innerHTML = "";

        for (let i = 0; i < desired; i++) {

            const drop = document.createElement("span");

            drop.className = "drop";
            drop.style.left = (Math.random() * 100) + "%";
            drop.style.animationDuration = (1.1 + Math.random() * 0.9) + "s";
            drop.style.animationDelay = (Math.random() * 3) + "s";
            drop.style.opacity = (0.3 + Math.random() * 0.5).toFixed(2);

            layer.appendChild(drop);

        }

        layer.dataset.count = String(desired);

    }

    layer.style.opacity = probability < 15 ? "0" : "1";

}

function updateClouds(cloudPercent) {

    const clouds = document.querySelector(".clouds");

    if (!clouds) return;

    clouds.style.setProperty("--cloud-opacity", (cloudPercent / 100).toFixed(2));

}

async function loadWeather() {

    try {

        const response = await fetch("/api/weather");

        const data = await response.json();

        if (data.status === "offline") {

            document.getElementById("warnings").innerHTML =
                "<div class='warning-item offline'><h4>❌ Mất kết nối</h4><p>Không lấy được dữ liệu thời tiết.</p></div>";

            return;
        }

        const current = data.current;

        animateNumber("temperature", current.temperature, 1, " °C");
        animateNumber("humidity", current.humidity, 0, " %");
        animateNumber("rain", current.rain_probability, 0, "");
        animateNumber("cloud", current.cloud, 0, " %");
        animateNumber("uv", current.uv, 2, "");
        animateNumber("wind", current.wind, 1, " km/h");

        document.getElementById("update").innerHTML =
            formatVNTime(current.time);

        // Vòng đo mưa ở khối hero
        setGauge(document.getElementById("rainDial"), current.rain_probability, 100);

        // Thanh mức của từng thẻ (thang đo tham khảo, không phải ngưỡng cảnh báo)
        setGauge(document.querySelector('[data-bar="humidity"] .bar'), current.humidity, 100);
        setGauge(document.querySelector('[data-bar="cloud"] .bar'), current.cloud, 100);
        setGauge(document.querySelector('[data-bar="uv"] .bar'), current.uv, 12);
        setGauge(document.querySelector('[data-bar="wind"] .bar'), current.wind, 40);

        // Nền động: mưa rơi + mây đậm nhạt theo dữ liệu thật
        updateRainLayer(current.rain_probability);
        updateClouds(current.cloud);

        // Glow nhẹ quanh khối hero khi rủi ro mưa cao
        const hero = document.getElementById("hero");
        if (hero) hero.classList.toggle("risk", current.rain_probability >= 60);

        const warningBox = document.getElementById("warnings");

        warningBox.innerHTML = "";

        if (data.warnings.length === 0) {

            warningBox.innerHTML =
                "<div class='warning-item safe'><h4>✅ An toàn</h4><p>Hiện chưa có cảnh báo.</p></div>";

        } else {

            data.warnings.forEach(w => {

                warningBox.innerHTML += `
                    <div class="warning-item alert">
                        <h4>${w.title}</h4>
                        <p>${w.message}</p>
                    </div>
                `;

            });

        }

        updateFavicon(data.warnings);

    } catch (e) {

        console.log(e);

    }

}

// ==========================================
// Favicon đổi theo thời tiết hiện tại
// ==========================================

// Thứ tự ưu tiên khi có nhiều cảnh báo cùng lúc
const FAVICON_PRIORITY = ["heat", "wind", "rain", "uv"];

function updateFavicon(warnings) {

    let type = "normal";

    if (warnings && warnings.length > 0) {

        const types = warnings.map(w => w.type);

        type = FAVICON_PRIORITY.find(t => types.includes(t)) || warnings[0].type;

    }

    const href = `/static/weather-icons/favicon-${type}-32.png`;

    let link = document.querySelector("link[rel='icon']");

    if (!link) {
        link = document.createElement("link");
        link.rel = "icon";
        document.head.appendChild(link);
    }

    link.type = "image/png";
    link.href = href;

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
