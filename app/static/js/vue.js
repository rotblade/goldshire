var app = new Vue({
  el: '#app',
  data: {
    dataHeaders: stockHeaders,
    cnyData: stocks['cny'],
    hkdData: stocks['hkd'],
    usdData: stocks['usd'],
    market: '',
    stock: '',
  },
  computed: {
    stockList: function() {
      stockList = {}
      switch(this.market) {
        case 'A股市场':
          for (const key in this.cnyData) {
            stockList[key] = this.cnyData[key]['Name'];
          }
          break;
        case '港股市场':
          for (const key in this.hkdData) {
            stockList[key] = this.hkdData[key]['Name'];
          }
          break;
        case '美股市场':
          for (const key in this.usdData) {
            stockList[key] = this.usdData[key]['Name'];
          }
          break;
        default:
      }
      return stockList;
    },
    stockData: function() {
      if (!isNaN(parseInt(this.stock))) {
        if (symbol.length == 6) {
          return this.cnyData[this.stock];
        }
        else {
          return this.hkdData[this.stock];
        }
      }
      else {
        return this.usdData[this.stock];
      }
      return {};
    },
  },
  created: function() {
  },
  methods: {
    getStock: function(symbol) {
      this.stock = symbol;
    },
    getStocks: function(api_url) {
      axios.get(api_url).then(response => {
        console.log(response.data)
      })
      .catch(e => {
      })
    }
  }
})
