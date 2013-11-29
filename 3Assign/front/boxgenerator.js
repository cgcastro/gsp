//	Simple code to create some boxes to display as blocks in the
//	blocks-world domain.

boxes = [];
var holdingBox;

function getBox(boxWidth, className) {
	//	Creates a box div : for blocks
	
	var box = document.createElement('div');
	box.style.width = boxWidth + 'px';
	box.style.height = box.style.width;
	box.style.lineHeight = box.style.height;
	box.className = className;

	return box;
}

function setBoxXY(box, boxWidth, x, y) {
	//	Call by value here, but should work anyway.
	//	I guess this is because the 'box' parameter is a mutable
	//	object.
	//	xy notation as used commonly in image processing : x goes
	//	rightward, y downward. Both start from 0.
	//	Will be awkward to handle blocks with
	//	this, but hopefully the divs will line up properly at least...
	
	box.style.top = (boxWidth * y) + 'px';
	box.style.left = (boxWidth * x) + 'px';
	box.id = 'box' + x.toString() + '-' + y.toString();
}

function toggleBox(boxElement) {
	//	Probably works because 'boxElement' is a mutable object, a
	//	reference to which was passed by value.
	
	if(boxElement.className == 'empty-box')
		boxElement.className = 'full-box';
	else
		boxElement.className = 'empty-box';
}

function setBoxType(boxElement, className) {
	boxElement.className = className;
}

function setBoxText(boxElement, text) {
	boxElement.innerHTML = text;
}

function createBoxes() {
	var currentState = document.getElementById('current-state');
	
	var width = 300;	//	total width of grid
	var numBlocksPerLine = 5;
	var boxWidth = width / numBlocksPerLine;

	var boxes = [];

	for(var i = 0; i < numBlocksPerLine; i++) {
		boxes.push([]);
		for(var j = 0; j < numBlocksPerLine; j++) {
			var box = getBox(boxWidth, 'empty-box');
			setBoxXY(box, boxWidth, i, j);
			currentState.appendChild(box);
			boxes[i].push(box);
		}
	}
	return boxes;
}

function displayBoxes(boxes, boxMap) {
	for(var i = 0; i < boxes.length; i++) {
		for(var j = 0; j < boxes[i].length; j++) {
			setBoxType(boxes[i][j], 'empty-box');
		}
	}
	for(var block in boxMap) {
		setBoxType(boxMap[block]['div'], 'full-box');
		setBoxText(boxMap[block]['div'], block);
	}
}

function getBoxMap(state, boxes) {
	var boxMap = {};
	
	var currentX = Math.floor(boxes.length / 2);
	var directionCumMultiplier = 1;

	for(var i = 0; i < state['onTable'].length; i++) {
		boxMap[state['onTable'][i]] = {};
		boxMap[state['onTable'][i]]['div'] = boxes[currentX][boxes.length - 1];	//	at the bottom
		boxMap[state['onTable'][i]]['xy'] = [currentX, boxes.length - 1];

		//	Some funky update rule, this!
		currentX = currentX + directionCumMultiplier;
		directionCumMultiplier = -(directionCumMultiplier + 1);	//	watch the minus
	}

	var left = true;
	while(left) {
		left = false;
		for(var i = 0; i < state['on'].length; i++) {
			if(state['on'][i][1] in boxMap) {
				boxMap[state['on'][i][0]] = {};
				var below = state['on'][i][1];
				var belowMap = boxMap[below];
				var boxXY =  [belowMap['xy'][0], belowMap['xy'][1] - 1];
				boxMap[state['on'][i][0]]['xy'] = boxXY;
				boxMap[state['on'][i][0]]['div'] = boxes[boxXY[0]][boxXY[1]];
			} else {
				left = true;
			}
		}
	}
	if(state['holding'].length != 0) {
		boxMap[state['holding'][0]]['div'] = holdingBox;
	}

	return boxMap;
}

function mainHandler() {
	boxes = createBoxes();
	holdingBox = document.getElementById('holding-box');
	var boxMap = {};

	displayBoxes(boxes, boxMap);
}

function displayStateSequence(seq) {
	if(seq.length == 0) return;

	var delay = 1500;	//	how much time a particular state shows up.
	var state = seq[0];
	var boxMap = getBoxMap(state, boxes);

	displayBoxes(boxes, boxMap);
	setTimeout(displayStateSequence(seq.slice(1,seq.length), delay);
}

function sendState() {
	var initOn = eval(document.getElementById('on-i').value);
	var initClear = eval(document.getElementById('clear-i').value);
	var initHolding = eval(document.getElementById('holding-i').value);
	var initOnTable = eval(document.getElementById('onTable-i').value);
	var initArmEmpty = eval(document.getElementById('armEmpty-i').value);
	var initState = {"on": initOn, "clear": initClear, "holding": initHolding, "onTable": initOnTable, "armEmpty" : initArmEmpty};

	var desiredOn = eval(document.getElementById('on-d').value);
	var desiredClear = eval(document.getElementById('clear-d').value);
	var desiredHolding = eval(document.getElementById('holding-d').value);
	var desiredOnTable = eval(document.getElementById('onTable-d').value);
	var desiredArmEmpty = eval(document.getElementById('armEmpty-d').value);
	var desiredState = {"on": desiredOn, "clear": desiredClear, "holding": desiredHolding, "onTable": desiredOnTable, "armEmpty" : desiredArmEmpty};
	
	var localUrl = "http://localhost:4444/";
	var sentData = {'start': initState, 'goal': desiredState};
	console.log(JSON.stringify(sentData));

	$.ajax({
		url: localUrl,
		type: 'POST',
		data: JSON.stringify(sentData),
		success: function(result) {
			result = JSON.parse(result);
			console.log(result);
			if(result == []) {
				alert("No plan found! :-/");
			}
			displayStateSequence(result);
		}
	});
}

window.onload = mainHandler;
