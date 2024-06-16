document.querySelectorAll('.comment').forEach(item => {
    item.addEventListener('click', event => {
        item.style.order = -1; 
    });
    item.addEventListener('mouseenter', event => {
        item.style.backgroundColor = '#d6e6ff'; 
    });
    item.addEventListener('mouseleave', event => {
        item.style.backgroundColor = '#f9f9f9'; 
    });
});
