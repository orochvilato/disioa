function setInfiniteScroll(id,path,args,append) {
  
  if (infScroll!=undefined) {
      elem.innerHTML = "";
      infScroll.destroy()
  }
  var elem = document.getElementById(id);
  urlargs = Object.keys(args).map(function(k) {
    return encodeURIComponent(k) + "=" + encodeURIComponent(args[k]);
  }).join('&');
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

function showNuage(lex) {
    if (lex=='verbatim') {
        return
    }
    var div = document.getElementById("sourrounding_div_"+lex);
    var canvas = document.getElementById("wordcanvas_"+lex);

    canvas.height = div.offsetHeight;
    canvas.width  = div.offsetWidth;

    WordCloud(document.getElementById('wordcanvas_'+lex), {
        gridSize: Math.round(16 * document.getElementById('wordcanvas_'+lex).offsetWidth / 1024),
        weightFactor: function (size) {
            return 0.3*size;
        },
        list: wordlist[lex],
        color: function(word, weight) {
            if (weight < 50) {
                return '#82cde2';
            } else if (weight < 130) {
                return '#213558';
            }
            return '#ff0052';
        },
        backgroundColor: 'transparent'
    });
}

function drawNuages() {
    showNuage('noms');
    showNuage('verbes');
}
