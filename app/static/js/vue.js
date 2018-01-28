var app = new Vue({
  el: '#app',
  data: {
    url: stocks_url,
    dataHeaders: stockHeaders,
    cnyData: stocks['cny'],
    hkdData: stocks['hkd'],
    usdData: stocks['usd'],
    tradeHeaders: [],
    tradeData: [],
    market: '',
    stock: '',
  },
  computed: {
    stockHolding: function() {
      stockHolding = {'cny': 0, 'hkd': 0, 'usd': 0}
      for (const key in this.cnyData) {
        if (this.cnyData[key]['Qty']>0) {
            stockHolding['cny'] += 1
        }
      }
      for (const key in this.hkdData) {
        if (this.hkdData[key]['Qty']>0) {
            stockHolding['hkd'] += 1
        }
      }
      for (const key in this.usdData) {
        if (this.usdData[key]['Qty']>0) {
            stockHolding['usd'] += 1
        }
      }
      return stockHolding
    },

    stockList: function() {
      stockList = {}
      switch(this.market) {
        case 'cny':
          for (const key in this.cnyData) {
            stockList[key] = this.cnyData[key]['Name']
          }
          break
        case 'hkd':
          for (const key in this.hkdData) {
            stockList[key] = this.hkdData[key]['Name']
          }
          break
        case 'usd':
          for (const key in this.usdData) {
            stockList[key] = this.usdData[key]['Name']
          }
          break
        default:
      }
      return stockList
    },

    stockData: function() {
      stockData = {}
      if (this.stock.length>0) {
        switch(this.market) {
          case 'cny':
            stockData = this.cnyData[this.stock]
            break
          case 'hkd':
            stockData = this.hkdData[this.stock]
            break
          case 'usd':
            stockData = this.usdData[this.stock]
            break
          default:
        }
      }
      return stockData
    },

  },

  created: function() {
  },

  methods: {
    getStock: function(symbol, market) {
      this.stock = symbol
      this.market = market
      this.tradeHeaders = []
    },

    marketChanged: function() {
      this.stock = ''
      this.tradeHeaders=[]
    },

    stockChanged: function() {
      this.tradeHeaders=[]
    },

    getTrades: function() {
      trade_url = this.url+'?market='+this.market+'&symbol='+this.stock
      axios.get(trade_url).then(response => {
       // console.log(response.data)
       this.tradeHeaders = response.data[0]
       trades = response.data[1]
       for (i=0; i<trades.length; i++) {
           tdate = new Date(trades[i]['Date'])
           trades[i]['Date'] = tdate.toLocaleDateString()
       }
       this.tradeData = trades
      })
      .catch(e => {
      })
    }
  }
})
