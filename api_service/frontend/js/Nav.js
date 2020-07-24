

class ScrollController {
    constructor() {
        this.searchBox = document.querySelector(".header__banner--search");
        this.searchDot = document.querySelector(".search-dot");
        this.searchHidden = false
        this.searchDotClick = false
        this.listen()
    }

    listen() {
        window.addEventListener("scroll", (e) => {
           this.checkSearchScroll();
        });
        this.searchDot.addEventListener("click", (e) => {
           this.searchBox.removeAttribute("style")
            if (this.searchDotClick) {
                this.searchDotClick = false
                this.searchBox.style.display = "none"
            } else {
                this.searchBox.style.position = "fixed"
                this.searchDotClick = true
            }

        });
    }

    checkSearchScroll() {
        if (!this.isVisible(this.searchBox) && !this.searchHidden) {
            this.searchBox.style.display = "none"
            this.searchHidden = true
            this.searchDot.style.display = "flex"
        }
        if (window.scrollY == 0 && this.searchHidden) {
            this.searchHidden = false
            this.searchBox.removeAttribute("style");
            this.searchDot.removeAttribute("style");
        }


    }
    isVisible(el) {
        let rect = el.getBoundingClientRect();
        let elemTop = rect.top;
        let elemBottom = rect.bottom;

        // Only completely visible elements return true:
        let isVisible = (elemTop >= 0) && (elemBottom <= window.innerHeight);
        // Partially visible elements return true:
        //isVisible = elemTop < window.innerHeight && elemBottom >= 0;
        return isVisible;
        }
}


export default new ScrollController();