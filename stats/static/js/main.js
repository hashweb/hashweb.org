require([], function() {

	var margin = {top: 10, right: 10, bottom: 100, left: 100},
    width  = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

	var parseDate = d3.time.format("%a, %d %b %Y %H:%M:%S %Z").parse;

	var x = d3.time.scale().range([0, width]),
	    y = d3.scale.linear().range([height, 0]);

	var xAxis = d3.svg.axis().scale(x).orient("bottom"),
	    yAxis = d3.svg.axis().scale(y).orient("left");

	var brush = d3.svg.brush().on("brush", brushed);

	var area = d3.svg.area()
	    .interpolate("monotone")
	    .x(function(d) { return x(d.timestamp); })
	    .y0(height)
	    .y1(function(d) { return y(d.count); });

	var svg = d3.select("body").append("svg")
	    .attr("width", width + margin.left + margin.right)
	    .attr("height", height + margin.top + margin.bottom);

	svg.append("defs").append("clipPath")
	    .attr("id", "clip")
	    .append("rect")
	    .attr("width", width)
	    .attr("height", height);

	var focus = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	d3.json('getfullusercount', function (data) {
	    data.forEach(function(d) {
	      d.timestamp = parseDate(d.timestamp);
	    });

	  x.domain(d3.extent(data.map(function(d) { return d.timestamp; })));
	  y.domain([0, d3.max(data.map(function(d) { return d.count; }))]);

	  focus.append("path")
	       .datum(data)
	       .attr("clip-path", "url(#clip)")
	       .attr("d", area);

	  focus.append("g")
	       .attr("class", "x axis")
	       .attr("transform", "translate(0," + height + ")")
	       .call(xAxis);

	  focus.append("g")
	       .attr("class", "y axis")
	       .call(yAxis);
	});

  	function brushed() {
	    x.domain(brush.empty() ? x2.domain() : brush.extent());
	    focus.select("path").attr("d", area);
	    focus.select(".x.axis").call(xAxis);
 	}
});