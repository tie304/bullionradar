import axios from "axios";


class ProductSearch {
    constructor() {
        this.searchState = {gold: false, silver: false, price: {type: false, price: false}, size: false}
        this.goldCheckbox = document.getElementById("gold");
        this.silverCheckbox = document.getElementById("silver");
        this.gte= document.getElementById("gte");
        this.lte = document.getElementById("lte");
        this.searchBox = document.querySelector(".header__banner--search")
        this.priceSearch = document.getElementById("price_search");
        this.searchButton = document.getElementById("search");
        this.productDisplay = document.getElementById("search_results");
        this.productSizeSelect = document.getElementById("bullion_size");
        this.searchError = document.getElementById("search-error");
        this.spot = SPOT_PRICES // const
        this.products = []

        this.listen()

    }

    listen() {
        this.goldCheckbox.addEventListener("change", (e) => {
            this.searchState.gold = e.target.checked
        });
         this.silverCheckbox.addEventListener("change", (e) => {
            this.searchState.silver = e.target.checked
        });

         this.lte.addEventListener("change", (e) => {
             this.searchState.price.type = "lte"
         });

         this.gte.addEventListener("change", (e) => {
             this.searchState.price.type = "gte"
         });

         this.priceSearch.addEventListener("change", (e) => {
             this.searchState.price.price = parseFloat(e.target.value)
         });
         this.searchButton.addEventListener("click", (e) => {
             this.getProducts()
         });

        this.productSizeSelect.addEventListener("change", (e) => {
            this.searchState.size = e.target.value;
        })
    }



    constructFilters() {
        let query = {};
        const metals = []
        if (this.searchState.gold) {
            metals.push("gold")
        }
        if (this.searchState.silver) {
            metals.push("silver")
        }
        if (metals.length) {
            query.metals = metals
        }
        if (this.searchState.price.type && this.searchState.price.price) {
            query.price = this.searchState.price
        }
        if (this.searchState.size) {
            query["size"] = this.searchState.size
        }
        return query
    }

    getProducts () {
        const filters = this.constructFilters();
        axios.post("http://localhost:8000/api/products", filters).then((res) => {
            this.clearProducts();
            this.products = res.data;
            this.displayProducts();
            this.productDisplay.scrollIntoView({behavior: "smooth"});
        }).catch((error)=> {
            if (error.response.status === 500) {
              return this.setSearchError("Internal server error. Please contact bullionradar")
           }
           if (error.response.data.detail && !error.response.status === 500) {
               return this.setSearchError(error.response.data.detail)
             }
           return this.setSearchError(error.response.data.detail)
        });
    }

    setSearchError(value) {
        this.searchError.innerHTML = value
    }

    displayProducts() {
        if (!this.products.length) {
            this.productDisplay.style.display = "block"
            this.setSearchError("No products match your search")
        } else {
            this.setSearchError("")
            this.productDisplay.style.display = "flex"
            this.products.sort((a, b) => {
                return this.calculateCostPerUnit(a.size, a.price, a.type).overSpot - this.calculateCostPerUnit(b.size, b.price, b.type).overSpot;
            })
            this.products.forEach((p) => {
            const {costPerUnit, overSpot} = this.calculateCostPerUnit(p.size, p.price, p.type);
            const goldImg = "<img class='product-card__img' src='http://localhost:8000/static/images/gold-bars.png'/>"
            const silverImg = "<img class='product-card__img' src='http://localhost:8000/static/images/silver-bars.png'/>"
            const html =`
            <div class='product-card'>
            <div class="product-card__title">
                ${p.type == "silver"? silverImg : goldImg} <a class="product-card__link" href="${p.url}" target="_blank"> <h3 class="product-card__name"> ${p.name}</h3> </a>
            </div>                            
                <div class="product-card__price">Price: $${p.price}</div> 
                <div class="product-card__price"> Size: ${p.size}</div> 
                <div class="product-card__price"> Cost per ${p.size.replace(/[0-9]/g, '').replace(/[^\w\s]|_/g, "")}: $${costPerUnit.toFixed(2)}</div> 
                <div class="product-card__price">Total price over spot: $${overSpot.toFixed(2)} ( ${(overSpot / p.price).toFixed(2)}%)</div>                
                <div class="product-card__price"> In Stock: ${p.in_stock}</div>
                <br>
                <br>
                <div class="product-card__price">${p.description}</div>
            </div>
            `;
            this.productDisplay.insertAdjacentHTML("beforeend", html)
        });
        }
    }
    calculateCostPerUnit(size, price, type) {
        // Calculates price over spot
        const oz = size.indexOf("oz");
        const g = size.indexOf("g");
        const kg = size.indexOf("kg");

        const sizeValue = parseFloat(size);

        if (oz > 0) {
            let costPerUnit = price / sizeValue;
            let overSpot = (costPerUnit - this.spot[type].oz) * sizeValue
            return {costPerUnit, overSpot}
        }
        if (g > 0) {
            let costPerUnit = price / sizeValue;
            let overSpot = (costPerUnit - this.spot[type].oz) * sizeValue
            return {costPerUnit, overSpot}
        }
        if (kg > 0) {
             let costPerUnit = price / sizeValue;
            let overSpot = (costPerUnit - this.spot[type].oz) * sizeValue
            return {costPerUnit, overSpot}
        }
    }
    clearProducts() {
        this.productDisplay.innerHTML = ""
    }
}

export default new ProductSearch()