window.addEventListener('scroll', function() {
    var header = document.querySelector('header');
    var scrollPosition = window.scrollY || document.documentElement.scrollTop;
    var windowHeight = window.innerHeight;

    // Якщо користувач прокручує до середини сторінки
    if (scrollPosition > windowHeight) {
        header.classList.add('hidden'); // Додаємо клас для зникання
    } else {
        header.classList.remove('hidden'); // Видаляємо клас для відновлення видимості
    }
});
