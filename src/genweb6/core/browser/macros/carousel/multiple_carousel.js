var carousels = document.querySelectorAll('.template-multiple-carousel:not(.already-loaded)');

carousels.forEach((carousel) => {

    carousel.classList.add("already-loaded");

    var items = carousel.querySelectorAll('.carousel .carousel-item');

    items.forEach((el) => {

      const minPerSlide = 4;
      let next = el.nextElementSibling;

      for (var i=1; i<minPerSlide; i++) {
        if (!next) {
          next = items[0];
        }

        let cloneChild = next.cloneNode(true);
        el.appendChild(cloneChild.children[0]);
        next = next.nextElementSibling;
      }

    });

});
