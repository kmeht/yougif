$(function() {


	var currentFrame = 1;
	var totalFrames = $("#window #images img").length;
	var images = {}
	var imageData = []

	$("#images img:first-child").addClass("current");

	// Sets the size and position information for images.
	function updateFrameData(image) {
		var index = image.data('index');
		frameData = imageData[index][currentFrame] = {
			top : image.position().top,
			left : image.position().left,
			height : image.height(),
			width : image.width()
		};
	}

	// Update the image position and sizes on frame change.
	function updateImagePositions(forward) {
		$("#stage div.image").each(function() {
			var index = $(this).data('index');
			
			// If the frame is not listed, either add it going forward,
			// or hide the image going backward.
			if (!(currentFrame in imageData[index])) {
				if (forward && (currentFrame-1 in imageData[index])) {
					imageData[index][currentFrame] = {
						top: imageData[index][currentFrame-1].top,
						left: imageData[index][currentFrame-1].left,
						height: imageData[index][currentFrame-1].height,
						width: imageData[index][currentFrame-1].width
					};
				} else {
					$(this).css({display: 'none'});
					return;
				}
			}

			// Update the position of the image per the stored data.
			var data = imageData[index][currentFrame];
			$(this).css({
				top : data.top,
				left: data.left,
				height: data.height,
				width: data.width,
				display: 'block'
			});
		});
	}

	// Place a new image on the stage.
	function placeNewImage(name) {
		var data = images[name];
		
		// Generate and place the DOM element.
		var div = $('<div>');
		div.css({
			'background-image' : "url(" + data.url + ")",
			'height' : data.height,
			'width' : data.width,
			'position': 'absolute'
		});
		div.addClass("image");
		$("#stage").append(div);
		div.draggable({containment: "#stage", scrollable: false, stop: function() { updateFrameData($(this)) }});
		div.resizable({containment: "#stage", stop: function() { updateFrameData($(this)) }});
		div.data('index', imageData.length);

		// Add data about this element and this frame.
		var elementData = {};
		elementData.name = name;
		elementData[currentFrame] = {
			top: div.position().top,
			left: div.position().left,
			height: data.height,
			width: data.width
		};
		imageData.push(elementData);
	}
	
	// Inform the server about a new file dropped onto the toolbar.
	$(document).on("drop", "#toolbar", function(e) {
		e.stopPropagation();
		e.preventDefault();
		
		var file = e.originalEvent.dataTransfer.files[0];
		var uuid = window.location.pathname.split("/")[1];
		var name = file.name
		$.ajax({
			type: 'post',
			url: '/' + uuid + '/add_image/' + name,
			contentType: false,
			data: file,
			processData: false,
			success: function(data) {
				data = JSON.parse(data);
				images[data.name] = {
					url: data.url,
					height: data.height,
					width: data.width
				};
				var image = $('<img>');
				image
					.attr('src', data.url)
					.data('name', data.name)
					.attr('draggable', true);
				$("#toolbar").append(image);
			},
			error: function() {
				alert("there was an error...");
			}
		});
	});

	$(document).on("click", "#submit", function() {
		var uuid = window.location.pathname.split("/")[1];
		$.ajax({
			type: 'post',
			url: '/' + uuid + '/finish',
			contentType: 'application/json',
			data: JSON.stringify({
				images: imageData
			}),
			success: function(data) {
				console.log(data);
				window.location.href = data;
			},
			error: function() {
				console.log("there was some error");
			}
		});

		return false;
	});


	
	$(document).on("dragover", "#stage", function(e) {
		e.originalEvent.preventDefault();
	})

	$(document).on("drop", "#stage", function(e) {
		e.stopPropagation();
		placeNewImage(e.originalEvent.dataTransfer.getData('text'));

	});

	$(document).on("dragstart", "#toolbar img", function(e) {
		e.originalEvent.dataTransfer.setData('text', $(this).data('name'));
	});
	
	// Event handlers for selecting elements.
	$(document).on("click", "#stage .image", function(e) {
		$(this).addClass("selected");
		e.stopPropagation();
	})

	$(document).on("mousedown", "#stage .image", function(e) {
		$("#stage .image").each(function() {
			$(this).removeClass("selected");
		});
		$(this).addClass("selected");
		e.stopPropagation();
	});

	$(document).click(function(e) {
		$("#stage .image").each(function() {
			$(this).removeClass("selected");
		});
	});

	// Go to the previous image, if it exists.
	function handleLeftArrow() {
		var img = $("img.current");
		var prev = img.prev();
		if (prev.length > 0) {
			prev.addClass("current");
			img.removeClass("current");
			currentFrame -= 1;
			updateImagePositions();
		}
	}

	// Go to the next image, if it exists.
	function handleRightArrow() {
		var img = $("img.current");
		var next = img.next();
		if (next.length > 0) {
			next.addClass("current");
			img.removeClass("current");
			currentFrame += 1;
			updateImagePositions(true);
		}
	}

	function deleteSelectedImage() {
		var image = $("#stage .image.selected");
		if (image.length > 0) {
			delete imageData[image.data('index')][currentFrame];
			image.remove();
		}
	}

	// Register keyboard handlers.
	$(document).keydown(function(e) {
		switch (e.keyCode) {
			case 37: handleLeftArrow(); break;
			case 39: handleRightArrow(); break;
			case 8:
			case 46: deleteSelectedImage(); break;
		}
	});

});