class TinyTree {
  constructor(containerId, data) {
    this.container = document.getElementById(containerId);
    this.data = data;
    this.xmlns = "http://www.w3.org/2000/svg";
    
    this.options = {
      levelSpacing: 80,
      minSiblingSpacing: 10,
      padding: 10            
    };

    this.initCanvas();

    const resizeObserver = new ResizeObserver(() => {
      this.render(); 
    });
    resizeObserver.observe(this.container);
  }

  initCanvas() {
    this.svg = document.createElementNS(this.xmlns, "svg");
    this.svg.setAttribute("width", "100%");
    this.svg.setAttribute("height", "100%");
    this.svg.style.display = "block";
    
    this.drawGroup = document.createElementNS(this.xmlns, "g");
    this.svg.appendChild(this.drawGroup);
    this.container.appendChild(this.svg);
  }

  render() {
    while (this.drawGroup.firstChild) {
      this.drawGroup.removeChild(this.drawGroup.firstChild);
    }

    const rect = this.container.getBoundingClientRect();
    const width = Math.max(rect.width, 200);
    
    this.preprocessTree(this.data);
    
    const totalTreeWidth = this.data.subtreeWidth;
    this.drawNode(this.data, width / 2, 20, totalTreeWidth / 2, true);
  }

  preprocessTree(node) {
    const measureDiv = document.createElement("div");
    measureDiv.innerHTML = node.name;
    measureDiv.style.cssText = `
        display: inline-block;
        padding: 0px;
        font-family: sans-serif;
        font-size: 11px;
        text-align: center;
        line-height: 1.2;
        visibility: hidden;
        position: absolute;
        white-space: nowrap; 
    `;
    document.body.appendChild(measureDiv);

    node.boxWidth = Math.max(55, measureDiv.offsetWidth + this.options.padding);
    node.boxHeight = measureDiv.offsetHeight + this.options.padding;
    document.body.removeChild(measureDiv);

    if (node.children && node.children.length > 0) {
      let childrenWidth = 0;
      node.children.forEach((child) => {
        this.preprocessTree(child);
        childrenWidth += child.subtreeWidth;
      });
      
      childrenWidth += (node.children.length - 1) * this.options.minSiblingSpacing;
      node.subtreeWidth = Math.max(node.boxWidth, childrenWidth);
    } else {
      node.subtreeWidth = node.boxWidth;
    }
  }

  drawNode(node, x, y, range, isRoot = false) {
    const boxWidth = node.boxWidth;
    const boxHeight = node.boxHeight;

    let strokeColor = "#333";
    let textColor = "#333";
    const cleanName = node.name.split("<br>")[0].trim().toLowerCase();

    if (cleanName === "kb" || cleanName === "wgs" || cleanName === "esbl_wgs") {
      strokeColor = "#00AC6B";
      textColor = "#00AC6B";
    } else if (cleanName.startsWith("need")) {
      strokeColor = "#D68100";
      textColor = "#D68100";
    }

    if (node.children && node.children.length > 0) {
      const childY = y + this.options.levelSpacing;
      
      let totalSubtreeWidth = 0;
      node.children.forEach(child => totalSubtreeWidth += child.subtreeWidth);
      
      const totalSpacing = (node.children.length - 1) * this.options.minSiblingSpacing;
      const availableWidthForSubtrees = (range * 2) - totalSpacing;
      const scale = availableWidthForSubtrees / totalSubtreeWidth;
      const scaledGroupWidth = (totalSubtreeWidth * scale) + totalSpacing;
      
     let currentOffset = x - (scaledGroupWidth / 2);

      node.children.forEach((child) => {
        const allocatedWidth = child.subtreeWidth * scale;
        const childX = currentOffset + (allocatedWidth / 2);
        
        this.drawCurve(x, y + boxHeight, childX, childY);
        this.drawNode(child, childX, childY, allocatedWidth / 2);
        
        currentOffset += allocatedWidth + this.options.minSiblingSpacing;
      });
    }

    const rect = document.createElementNS(this.xmlns, "rect");
    rect.setAttribute("x", x - boxWidth / 2);
    rect.setAttribute("y", y);
    rect.setAttribute("width", boxWidth);
    rect.setAttribute("height", boxHeight);
    rect.setAttribute("fill", "white");
    rect.setAttribute("stroke", strokeColor);
    rect.setAttribute("rx", "4");
    this.drawGroup.appendChild(rect);

    const foreignObject = document.createElementNS(this.xmlns, "foreignObject");
    foreignObject.setAttribute("x", x - boxWidth / 2);
    foreignObject.setAttribute("y", y);
    foreignObject.setAttribute("width", boxWidth);
    foreignObject.setAttribute("height", boxHeight);

    const div = document.createElement("div");
    div.innerHTML = node.name; 
    div.setAttribute("style", `
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
        font-family: sans-serif;
        font-size: 11px;
        text-align: center;
        line-height: 1.2;
        color: ${textColor}; /* Applies dynamic theme font color */
        font-weight: ${textColor !== "#333" ? "600" : "normal"}; /* Makes colored text highly legible */
    `);

    foreignObject.appendChild(div);
    this.drawGroup.appendChild(foreignObject);
  }

  drawCurve(sx, sy, ex, ey) {
    const path = document.createElementNS(this.xmlns, "path");
    const my = (sy + ey) / 2;
    const d = `M${sx},${sy} C${sx},${my} ${ex},${my} ${ex},${ey}`;
    path.setAttribute("d", d);
    path.setAttribute("stroke", "#ccc");
    path.setAttribute("fill", "none");
    this.drawGroup.insertBefore(path, this.drawGroup.firstChild);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  const dataElement = document.getElementById('my-data-json');
  if (dataElement) {
    const rawData = JSON.parse(dataElement.textContent);
    new TinyTree("tree-container", rawData);
  }
});