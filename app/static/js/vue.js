var app = new Vue({
  el: '#app',
  data: {
    tblHeaders: [],
    cnyData: []
    hkdData: []
    usdData: []
  },
  created: function(){
  },
  methods: {
    getStocks: function(api_url) {
      axios.get(api_url).then(response => {
        console.log(response.data)
        this.tblHeaders = response.data[0]
        this.cnyData = response.data[1]['cny']
        this.hkdData = response.data[1]['hkd']
        this.usdData = response.data[1]['usd']
      })
      .catch(e => {
      })
    }
  },
  computed: {
  }
})
