define(function() {

var margin = {top: 20, right: 20, bottom: 40, left: 60},
    width = 960;
    height = 500;

var formatPercent = d3.format(".0%");

var x = d3.scale.ordinal()
    .rangeRoundBands([0, width], .1, 1);

var y = d3.scale.linear()
    .range([height, 0]);

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom")
    .tickSize(0, 0);

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left");

var svg = d3.select(".chattyUsers").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", 650)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

d3.json("getchattyusers", function(error, data) {
    jQuery('.loading-message').hide();
	  data.forEach(function(d) {
	    d.frequency = +d.frequency;
	  });

	  x.domain(data.map(function(d) { return d.user; }));
	  y.domain([0, d3.max(data, function(d) { return d.noOfMessages; })]);

	  svg.append("g")
	      .attr("class", "x axis")
	      .attr("transform", "translate(-12," + (height + 40) + ")")
	      .call(xAxis)
	      .selectAll('text')
	      		.attr("transform", function(d) {
                	return "rotate(-87)" 
                })



      d3.selectAll('.x line, .x path').remove();

	  svg.append("g")
	      .attr("class", "y axis")
	      .call(yAxis)
	    .append("text")
	      .attr("transform", "rotate(-90)")
	      .attr("y", 12)
	      .attr("dy", ".71em")
	      .style("text-anchor", "end")
	      .text("No Of Messages");

	  svg.selectAll(".bar")
	      .data(data)
	    .enter().append("rect")
	      .attr("class", "bar")
	      .attr("x", function(d) { return x(d.user); })
	      .attr("width", x.rangeBand())
	      .attr("y", function(d) { return y(d.noOfMessages); })
	      .attr("height", function(d) { return height - y(d.noOfMessages); })
	    .append("svg:title")
	    	.text(function(d, i) { return "Message count is " + d.noOfMessages; })

	  d3.select("input").on("change", change);

	  var sortTimeout = setTimeout(function() {

	    // d3.select("input").property("checked", true).each(change);
	  }, 2000);

	  function change() {
	    clearTimeout(sortTimeout);

	    // Copy-on-write since tweens are evaluated after a delay.
	    var x0 = x.domain(data.sort(this.checked
	        ? function(a, b) { return b.noOfMessages - a.noOfMessages; }
	        : function(a, b) { return d3.ascending(a.user, b.user); })
	        .map(function(d) { return d.user; }))
	        .copy();

	    var transition = svg.transition().duration(750),
	        delay = function(d, i) { return i * 50; };

	    transition.selectAll(".bar")
	        .delay(delay)
	        .attr("x", function(d) { return x0(d.user); });

	    transition.select(".x.axis")
	        .call(xAxis)
	      .selectAll("g")
	        .delay(delay);
	  }
	});
});