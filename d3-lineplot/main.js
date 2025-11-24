d3.selectAll("svg").remove();

// set dimensions and design
let width = 600;
    height = 400;

let margin = {
  top: 50,
  right: 50,
  bottom: 50,
  left: 50
}

let svg = d3.select('body')
  .append('svg')
  .attr('width', width)
  .attr('height', height)
  .style('background', 'lightyellow');  

// load data
d3.csv("yearly_avg_price_trends.csv").then(data => {

  // convert strings -> numbers
  data.forEach(d => {
    d.year = +d.Year;
    d.avg_price = +d.Avg_Price;
  });

  // define scales
  let xScale = d3.scaleLinear()
      .domain(d3.extent(data, d => d.year))
      .range([margin.left, width - margin.right]);

  let yScale = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.avg_price)])
      .range([height - margin.bottom, margin.top]);

  // draw axes
  svg.append("g")
  .attr("transform", `translate(0, ${height - margin.bottom})`)
  .call(d3.axisBottom(xScale)
    .tickValues(data.map(d => d.year))
    .tickFormat(d3.format("d")));

  svg.append("g")
    .attr("transform", `translate(${margin.left}, 0)`)
    .call(d3.axisLeft(yScale));

  // draw circles
  svg.selectAll("circle")
    .data(data)
    .enter()
    .append("circle")
    .attr("r", 4)
    .attr("cx", d => xScale(d.year))
    .attr("cy", d => yScale(d.avg_price))
    .attr("fill", "red");

  // line generator
  let line = d3.line()
    .x(d => xScale(d.year))
    .y(d => yScale(d.avg_price))
    .curve(d3.curveNatural);

  // draw line path
  svg.append("path")
    .datum(data)
    .attr("fill", "none")
    .attr("stroke", "red")
    .attr("stroke-width", 1.5)
    .attr("d", line);

});
