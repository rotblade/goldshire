Vue.component('grid-stocks', {
  template: '#grid-stocks-template',
  props: {
    data: Array,
    columns: Array
  },
  data: function() {
    /*
    var sortOrders = {}
    this.columns.forEach(function(key) {
      sortOrders[key] = 1
    })*/
    var sortOrders = {
      '代码': 1,
      '股票': 1,
      '币种': 1,
      '持仓数量': 1,
      '最后价格': 1,
      '盈亏': 1,
      '回报': 1
    }
    return {
      sortKey: '',
      sortOrders: sortOrders
    }
  },
  computed: {
    sortedData: function() {
      var sortKey = this.sortKey
      var order = this.sortOrders[sortKey] || 1
      var data = this.data
      if (sortKey) {
        data = data.slice().sort(function(a, b) {
          a = a[sortKey]
          b = b[sortKey]
          return (a === b ? 0 : a > b ? 1 : -1) * order
        })
      }
      return data
    }
  },
  methods: {
    sortBy: function(key) {
      this.sortKey=key
      if (!this.sortOrders[key])
        this.sortOrders[key] = 1
      else
        this.sortOrders[key] = this.sortOrders[key] * -1 
    }
  }
})


var app = new Vue({
  el: '#app',
  data: {
    gridColumns: [],
    gridData: []
  },
  created: function(){
  },
  methods: {
    getStocks: function(api_url) {
      axios.get(api_url).then(response => {
        //console.log(response.data)
        this.gridColumns = response.data[0]
        this.gridData = response.data[1]
      })
      .catch(e => {
      })
    }
  },
  computed: {
  }
})
