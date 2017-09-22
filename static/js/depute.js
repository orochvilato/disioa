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


function initHemicycle(place) {
    var svgDoc = svg.contentDocument;
    $.each(svgDoc.getElementsByTagName('a'), function() {
       $(this).attr('href',"depute/index/"+$(this).attr('href'));
    });
    var styleElement = svgDoc.createElementNS("http://www.w3.org/2000/svg", "style");
    styleElement.textContent = "#p"+place+" { fill:  #ff0052; stroke-width:5px; stroke: #ff0052;}"; // add whatever you need here
    svgDoc.getElementById('defs').appendChild(styleElement);  
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

    // Calendrier
        function genCalendar() {
            var width = document.getElementById('calendar').offsetWidth,
                yearHeight = width / 7,
                height = yearHeight,
                cellSize = yearHeight / 8;

            var percent = d3.format(".1%"),
                format = d3.timeFormat("%Y-%m-%d");

            var color = d3.scaleQuantize()
                .domain([.0, 1.0])
                .range(d3.range(5).map(function(d) { return "q" + d + "-5"; }));

            var svgcal = d3.select("#calendar").selectAll("svg")
                .data(d3.range(2017, 2018))
              .enter().append("svg")
                .attr("width", width)
                .attr("height", height+20)
                .attr("class", "RdYlGn")
              .append("g")
                .attr("transform", "translate(" + ((width - cellSize * 53) / 2) + "," + (20+height - cellSize * 7 - 1) + ")");

            svgcal.append("text")
                .attr("transform", "translate(-6," + cellSize * 3.5 + ")rotate(-90)")
                .style("text-anchor", "middle")
                .text(function(d) { return d; });

            var rect = svgcal.selectAll(".day")
                .data(function(d) { return d3.timeDays(new Date(d, 0, 1), new Date(d + 1, 0, 1)); })
              .enter().append("rect")
                .attr("class", "day")
                .attr("width", cellSize)
                .attr("height", cellSize)
                .attr("x", function(d) { return d3.timeMonday.count(d3.timeYear(d), d) * cellSize; })
                .attr("y", function(d) { return ((d.getDay()+6)%7) * cellSize; })
                .datum(format);

            rect.append("title")
                .text(function(d) { return d; });

            svgcal.selectAll(".month")
                .data(function(d) { return d3.timeMonths(new Date(d, 0, 1), new Date(d + 1, 0, 1)); })
              .enter().append("text").text(monthLabel).style("font-size:10px;", "middle").attr("transform",monthLabelTransform);
            function monthLabel(t0) {
                return Array('JAN','FEV','MAR','AVR','MAI','JUN','JUI','AOU','SEP','OCT','NOV','DEC')[t0.getMonth()];
            }
            function monthLabelTransform(t0) {
              var t1 = new Date(t0.getFullYear(), t0.getMonth() + 1, 0),
                  d0 = ((t0.getDay()+6)%7), w0 = d3.timeMonday.count(d3.timeYear(t0), t0)
                  d1 = ((t1.getDay()+6)%7), w1 = d3.timeMonday.count(d3.timeYear(t1), t1);
              return "translate("+(2+w0)*cellSize+",-5)";
            }

            svgcal.selectAll(".month")
                .data(function(d) { return d3.timeMonths(new Date(d, 0, 1), new Date(d + 1, 0, 1)); })
              .enter().append("path")
                .attr("class", "month")
                .attr("d", monthPath);


            
            var data = d3.nest()
                .key(function(d) { return d.date; })
                .rollup(function(d) { return d[0].pct; })
                .map(csv);

              rect.filter(function(d) { return data.has(d); })
                  .attr("class", function(d) { return "day " + color(data.get(d)); })
                .select("title")
                  .text(function(d) { return d + ": " + percent(data.get(d)); });

            function monthPath(t0) {
              var t1 = new Date(t0.getFullYear(), t0.getMonth() + 1, 0),
                  d0 = ((t0.getDay()+6)%7), w0 = d3.timeMonday.count(d3.timeYear(t0), t0)
                  d1 = ((t1.getDay()+6)%7), w1 = d3.timeMonday.count(d3.timeYear(t1), t1);
              return "M" + (w0 + 1) * cellSize + "," + d0 * cellSize
                  + "H" + w0 * cellSize + "V" + 7 * cellSize
                  + "H" + w1 * cellSize + "V" + (d1 + 1) * cellSize
                  + "H" + (w1 + 1) * cellSize + "V" + 0
                  + "H" + (w0 + 1) * cellSize + "Z";
            }
        }
