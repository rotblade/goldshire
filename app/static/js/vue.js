var app = new Vue({
  el: '#app',
  data: {
    tblHeaders: [],
    cnyData: [],
    hkdData: [],
    usdData: [],
  },
  created: function(){
  },
  methods: {
    getStocks: function(api_url) {
      axios.get(api_url).then(response => {
        console.log(response.data)
      })
      .catch(e => {
      })
    }
  },
  computed: {
  }
})
