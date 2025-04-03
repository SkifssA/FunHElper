document.addEventListener('DOMContentLoaded', () => {
    const table = document.getElementById('anime-table');
    const rows = table.getElementsByTagName('tr');
    const addModal = document.getElementById('add-modal');
    const addAnimeBtn = document.getElementById('add-anime-btn');
    const cancelBtn = document.getElementById('cancel-btn');
    const loadAnimeBtn = document.getElementById('load-anime-btn');
    const markAsWatchedBtn = document.getElementById('mark-as-watched-btn');
    const openLinkBtn = document.getElementById('open-link-btn');
    const deleteAnimeBtn = document.getElementById('delete-anime-btn');
    const linkModal = document.getElementById('link-modal');
    const closeLinkModalBtn = document.getElementById('close-link-modal');
    const originalLink = document.getElementById('original-link');
    const vkLink = document.getElementById('vk-link');

    let selectedRowId = null;

    function setSelectedRowId(id) {
        selectedRowId = id;
    }

    function getSelectedRowId() {
        return selectedRowId;
    }
    
    navigator.serviceWorker.ready.then(function (registration) {
      return registration.pushManager.getSubscription().then(function (subscription) {
        if (subscription) {
          return subscription.unsubscribe();
        }
      });
    });
    
    // Проверяем поддержку уведомлений
    if (!("serviceWorker" in navigator)) {
      console.log("Service Worker не поддерживается.");
    } else if (!("PushManager" in window)) {
      console.log("Push API не поддерживается.");
    } else {
      // Регистрируем Service Worker
      navigator.serviceWorker.register("/static/js/service-worker.js").then(function (registration) {
        console.log("Service Worker зарегистрирован.");

        // Запрашиваем разрешение на уведомления
        Notification.requestPermission().then(function (permission) {
          if (permission === "granted") {
            // Подписываемся на Push-уведомления
            registration.pushManager.subscribe({
              userVisibleOnly: true,
              applicationServerKey: urlBase64ToUint8Array("BBrW-SxtLS_RPHS8nm6PGMo9XMO27VVNI7dAVjCngbr-zA5I81hKPqF81jaz2v6ce_SGXcV8XYEDM85Pv3dqDrk")
            }).then(function (subscription) {
              console.log("Подписка успешно создана:", subscription);

              // Отправляем подписку на сервер
              fetch("/anime/save-subscription", {
                method: "POST",
                headers: {
                  "Content-Type": "application/json"
                },
                body: JSON.stringify(subscription)
              }).then(function (response) {
                console.log("Подписка сохранена на сервере.");
              });
            });
          }
        });
      });
    }

    // Функция для преобразования VAPID-ключа
    function urlBase64ToUint8Array(base64String) {
      const padding = "=".repeat((4 - base64String.length % 4) % 4);
      const base64 = (base64String + padding).replace(/\-/g, "+").replace(/_/g, "/");
      const rawData = window.atob(base64);
      const outputArray = new Uint8Array(rawData.length);
      for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
      }
      return outputArray;
    }
    
    // Закрытие модальных окон
    cancelBtn.addEventListener('click', () => addModal.style.display = 'none');
    closeLinkModalBtn.addEventListener('click', () => linkModal.style.display = 'none');
    window.addEventListener('click', (event) => {
        if (event.target === addModal || event.target === linkModal) {
            addModal.style.display = 'none';
            linkModal.style.display = 'none';
        }
    });

    // Открытие модального окна для добавления аниме
    addAnimeBtn.addEventListener('click', () => addModal.style.display = 'block');

    // Добавление аниме
    loadAnimeBtn.addEventListener('click', () => {
        const url = document.getElementById('anime-url').value.trim();
        if (url) {
            fetch('/anime/add-anime', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url }),
            })
                .then(response => response.json())
                .then(data => {
                    // alert(data.message);
                    location.reload();
                })
                .catch(() => alert('Ошибка при добавлении аниме'));
        } else {
            alert('Введите URL аниме!');
        }
        addModal.style.display = 'none';
    });

    // Выбор строки таблицы
    table.addEventListener('click', (event) => {
        const clickedRow = event.target.closest('tr');
        if (clickedRow && clickedRow.tagName === 'TR') {
            for (const row of rows) row.classList.remove('selected-row');
            clickedRow.classList.add('selected-row');
            setSelectedRowId(clickedRow.dataset.id);
            markAsWatchedBtn.disabled = false;
            openLinkBtn.disabled = false;
            deleteAnimeBtn.disabled = false;
        } else {
            markAsWatchedBtn.disabled = true;
            openLinkBtn.disabled = true;
            deleteAnimeBtn.disabled = true;
        }
    });

    // Отметка аниме как просмотренного
    markAsWatchedBtn.addEventListener('click', () => {
        const id = getSelectedRowId();
        if (!id) return alert('Выберите строку!');
        fetch('/anime/mark-as-watched', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id }),
        })
            .then(response => response.json())
            .then(data => {
                // alert(data.message);
                location.reload();
            })
            .catch(() => alert('Ошибка при отметке аниме как просмотренного'));
    });

    // Открытие ссылок
    openLinkBtn.addEventListener('click', () => {
        const selectedRow = document.querySelector('#anime-table tr.selected-row');
        if (!selectedRow) return alert('Выберите строку!');
        const url = selectedRow.dataset.url;
        const name = selectedRow.dataset.name;
        const episodeCount = selectedRow.dataset.episodecount || 'все';
        if (url && name) {
            const vkSearchUrl = `https://vkvideo.ru/?q=${encodeURIComponent(name)}%20аниме%20все%20серии%201-${episodeCount}`;
            originalLink.href = url;
            originalLink.textContent = 'Оригинальная ссылка';
            vkLink.href = vkSearchUrl;
            vkLink.textContent = 'Поиск на VK';
            linkModal.style.display = 'block';
        } else {
            alert('Ссылка или название отсутствуют!');
        }
    });

    // Удаление аниме
    deleteAnimeBtn.addEventListener('click', () => {
        const id = getSelectedRowId();
        if (!id) return alert('Выберите аниме для удаления!');
        if (confirm('Вы уверены, что хотите удалить это аниме?')) {
            fetch('/anime/delete-anime', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id }),
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const selectedRow = document.querySelector('#anime-table tr.selected-row');
                        if (selectedRow) selectedRow.remove();
                        // alert(data.message);
                        deleteAnimeBtn.disabled = true;
                    } else {
                        alert('Ошибка при удалении аниме');
                    }
                })
                .catch(() => alert('Ошибка при удалении аниме'));
        }
    });
});