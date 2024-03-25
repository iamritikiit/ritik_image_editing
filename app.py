from flask import Flask, render_template, request, redirect, url_for
from PIL import Image, ImageOps, ImageFilter

app = Flask(__name__)


# Function to apply filters
def apply_filter(image_path, filter_name, **kwargs):
    image = Image.open(image_path)

    # Convert RGBA image to RGB mode
    if image.mode == "RGBA":
        image = image.convert("RGB")

    if filter_name == "grayscale":
        image = image.convert("L")
    elif filter_name == "invert":
        image = ImageOps.invert(image)
    elif filter_name == "blur":
        image = image.filter(ImageFilter.BLUR)
    elif filter_name == "rotate":
        angle = kwargs.get("angle", 0)  # Default angle is 0 if not provided
        image = image.rotate(angle)
    elif filter_name == "emboss":  # Add emboss filter
        image = image.filter(ImageFilter.EMBOSS)
    elif filter_name == "crop":
        # Get crop parameters
        left = int(kwargs.get("left", 0))
        upper = int(kwargs.get("upper", 0))
        right = int(kwargs.get("right", image.width))
        lower = int(kwargs.get("lower", image.height))

        # Validate crop parameters
        left = max(0, min(left, image.width - 1))  # Ensure left is within bounds
        upper = max(0, min(upper, image.height - 1))
        right = max(left + 1, min(right, image.width))  # Ensure right is within bounds
        lower = max(upper + 1, min(lower, image.height))

        # Crop the image
        image = image.crop((left, upper, right, lower))

    # Add more filter options as needed

    return image


# Route to display the upload form
@app.route("/")
def index():
    return render_template("index.html")


# Route to handle image upload and apply filters
@app.route("/upload", methods=["POST"])
def upload():
    if request.method == "POST":
        # Get the uploaded file
        uploaded_file = request.files["file"]

        if uploaded_file.filename != "":
            # Save the uploaded file
            image_path = "static/uploads/" + uploaded_file.filename
            uploaded_file.save(image_path)

            # Get the selected filter
            selected_filter = request.form["filter"]

            # Additional parameters for rotate and crop filters
            kwargs = {}
            if selected_filter == "rotate":
                kwargs["angle"] = int(request.form.get("angle", 0))
            elif selected_filter == "crop":
                kwargs["left"] = int(request.form.get("left", 0))
                kwargs["upper"] = int(request.form.get("upper", 0))
                kwargs["right"] = int(
                    request.form.get("right", Image.open(image_path).width)
                )
                kwargs["lower"] = int(
                    request.form.get("lower", Image.open(image_path).height)
                )

            # Apply the selected filter
            filtered_image = apply_filter(image_path, selected_filter, **kwargs)

            # Save the filtered image
            filtered_image_path = "static/uploads/filtered_" + uploaded_file.filename
            filtered_image.save(filtered_image_path)

            # Pass the image paths to the template for display
            return render_template(
                "result.html",
                original_image=image_path,
                filtered_image=filtered_image_path,
            )

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
