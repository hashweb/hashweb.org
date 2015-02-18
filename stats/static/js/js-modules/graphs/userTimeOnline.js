define(function() {

var margin = {top: 20, right: 20, bottom: 60, left: 40},
    width = 500 - margin.left - margin.right,
    height = 200 - margin.top - margin.bottom;

var formatPercent = d3.format(".0%");

var x = d3.scale.ordinal()
    .rangeRoundBands([0, width], .1, 1);

var y = d3.scale.linear()
    .range([height, 0]);

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var user = $('.page-wrap').data('user');

var svg = d3.select(".time-online").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

d3.json("/stats/getusertimeonline/" + user, function(error, data) {
        jQuery('.loading-message').hide();
	  data.forEach(function(d) {
	    d.frequency = +d.frequency;
	  });

	  x.domain(data.map(function(d) { return d.time; }));
	  y.domain([0, d3.max(data, function(d) { return d.perc; })]);

	  svg.append("g")
	      .attr("class", "x axis")
	      .attr("transform", "translate(-10," + (height + 30)+ ")")
	      .call(xAxis)
	      .selectAll('text')
	      		.attr("transform", function(d) {
                	return "rotate(-90)" 
                })

	  svg.selectAll(".bar")
	      .data(data)
	    .enter().append("rect")
	      .attr("class", "bar")
	      .attr("x", function(d) { return x(d.time); })
	      .attr("width", x.rangeBand())
	      .attr("y", function(d) { return y(d.perc); })
	      .attr("height", function(d) { return height - y(d.perc); })
	    .append("svg:title")
	    	.text(function(d, i) { return d.perc + '%'; })

	  // d3.select("input").on("change", change);

	  // var sortTimeout = setTimeout(function() {
	  //   d3.select("input").property("checked", true).each(change);
	  // }, 2000);
    // Hopefully this no longer gets called...
	  function change() {
	    clearTimeout(sortTimeout);

	    // Copy-on-write since tweens are evaluated after a delay.
	    var x0 = x.domain(data.sort(this.checked
	        ? function(a, b) { return b.perc - a.perc; }
	        : function(a, b) { return d3.ascending(a.perc, b.perc); })
	        .map(function(d) { return d.time; }))
	        .copy();

	    var transition = svg.transition().duration(750),
	        delay = function(d, i) { return i * 50; };

	    transition.selectAll(".bar")
	        .delay(delay)
	        .attr("x", function(d) { return x0(d.time); });

	    transition.select(".x.axis")
	        .call(xAxis)
	      .selectAll("g")
	        .delay(delay);
	  }
	});
});