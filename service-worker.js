const CACHE_NAME = "tweather-v1";

self.addEventListener("install", (event) => {

    console.log("Service Worker Installed");

    self.skipWaiting();

});

self.addEventListener("activate", (event) => {

    console.log("Service Worker Activated");

    event.waitUntil(

        caches.keys().then(keys => {

            return Promise.all(

                keys.map(key => {

                    if (key !== CACHE_NAME) {

                        return caches.delete(key);

                    }

                })

            );

        })

    );

});

self.addEventListener("push", (event) => {

    let data = {

        title: "T-Weather",

        body: "Có cảnh báo thời tiết.",

        icon: "/static/icon.png",

        badge: "/static/icon.png"

    };

    if (event.data) {

        data = event.data.json();

    }

    event.waitUntil(

        self.registration.showNotification(

            data.title,

            {

                body: data.body,

                icon: data.icon || "/static/icon.png",

                badge: data.badge || "/static/icon.png",

                vibrate: [200, 100, 200],

                requireInteraction: true,

                tag: "tweather-alert"

            }

        )

    );

});

self.addEventListener("notificationclick", (event) => {

    event.notification.close();

    event.waitUntil(

        clients.matchAll({

            type: "window",

            includeUncontrolled: true

        }).then(windowClients => {

            for (const client of windowClients) {

                if ("focus" in client) {

                    return client.focus();

                }

            }

            if (clients.openWindow) {

                return clients.openWindow("/");

            }

        })

    );

});