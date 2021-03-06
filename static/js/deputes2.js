function setInfiniteScroll(id,path,args,append,urlupdate,countid) {
  var elem = document.getElementById(id);
  var urlargs = '';
  
  if (!jQuery.isEmptyObject(args) ){
      urlargs = Object.keys(args).filter(function(k) { return args[k]!='';}).map(function(k) {
        return encodeURIComponent(k) + "=" + encodeURIComponent(args[k]);
      }).join('&');
  }
  if (urlupdate) {
      console.log('push');
      window.history.pushState({},"",'?'+urlargs);
  }
  // récupère le nombre de résultats
  if (countid) {
      $.getJSON( path+'?'+urlargs+"&count=1", function( data ) {
          if (data['compl']!=undefined) {
              $("#"+countid+"-compl").html(data['compl']);
          }
          $("#"+countid).html(data['count']);
      });
  }
  var infScroll = new InfiniteScroll( elem, {
  // options
  path: path+'/{{#}}?'+urlargs,
  checkLastPage: '.pagination__next',
  append: append,
  history: false,
  prefill: true
  });
  return infScroll
}
$('.deputes-filters select').change( function() { params[$(this).attr('name')]=this.value; top_IS=go_IS(); });

var search = document.getElementById("deputes-searchbutton");
function launchSearch() {
        top_IS = go_IS();
}

document.getElementById("deputes-searchtext").addEventListener("input", function(e) {
    params['txt'] =this.value;
});
document.getElementById("deputes-search").addEventListener("keypress", function(e) {
     if ((e.which && e.which == 13) || (e.keyCode && e.keyCode == 13)) {
          e.preventDefault();
          launchSearch();
     }
});
