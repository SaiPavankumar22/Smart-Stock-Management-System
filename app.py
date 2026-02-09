from flask import Flask, render_template, request, redirect, jsonify, flash, session
import csv
import io
import secrets

from services.inventory_service import inventory_service

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate secure secret key


# -----------------------
# HOME PAGE
# -----------------------
@app.route("/")
def home():
    try:
        stats = inventory_service.get_dashboard_stats()
        alerts = inventory_service.get_alerts()
        
        return render_template(
            "home.html",
            total_items=stats.get("total_items", 0),
            low_stock_count=len(alerts.get("low_stock", [])),
            dead_stock_count=len(alerts.get("dead_stock", [])),
            critical_stock_count=len(alerts.get("critical_stock", [])),
            total_sales=stats.get("total_sales", 0),
            total_value=f"{stats.get('total_stock_value', 0):,.2f}",
            alerts=alerts
        )
    except Exception as e:
        flash(f"Error loading dashboard: {str(e)}", "error")
        return render_template(
            "home.html",
            total_items=0,
            low_stock_count=0,
            dead_stock_count=0,
            critical_stock_count=0,
            total_sales=0,
            total_value="0.00",
            alerts={"dead_stock": [], "critical_stock": [], "low_stock": [], "total_alerts": 0}
        )


# -----------------------
# INVENTORY LIST
# -----------------------
@app.route("/inventory")
def inventory():
    items = inventory_service.list_items()
    alerts = inventory_service.get_alerts()
    return render_template("inventory.html", items=items, alerts=alerts)


# -----------------------
# ADD ITEM PAGE
# -----------------------
@app.route("/add-item", methods=["GET", "POST"])
def add_item():
    if request.method == "GET":
        return render_template("add_item.html")
    
    try:
        inventory_service.add_item(request.form)
        flash(f"✓ Product '{request.form.get('name')}' added successfully!", "success")
    except Exception as e:
        flash(f"✗ Error adding product: {str(e)}", "error")
    
    return redirect("/inventory")


# -----------------------
# EDIT ITEM
# -----------------------
@app.route("/edit-item/<object_id>", methods=["GET", "POST"])
def edit_item(object_id):
    item = inventory_service.get_item(object_id)

    if not item:
        flash("✗ Item not found", "error")
        return redirect("/inventory")

    if request.method == "GET":
        return render_template("edit_item.html", item=item)

    try:
        inventory_service.update_item(object_id, request.form)
        flash(f"✓ Product '{request.form.get('name')}' updated successfully!", "success")
    except Exception as e:
        flash(f"✗ Error updating product: {str(e)}", "error")
    
    return redirect("/inventory")


# -----------------------
# DELETE ITEM
# -----------------------
@app.route("/delete-item/<object_id>")
def delete_item(object_id):
    try:
        item = inventory_service.get_item(object_id)
        item_name = item.get("name", "Item") if item else "Item"
        inventory_service.delete_item(object_id)
        flash(f"✓ Product '{item_name}' deleted successfully!", "success")
    except Exception as e:
        flash(f"✗ Error deleting product: {str(e)}", "error")
    
    return redirect("/inventory")


# -----------------------
# LOW STOCK PAGE
# -----------------------
@app.route("/low-stock")
def low_stock():
    low_items = inventory_service.low_stock_items()
    critical_items = inventory_service.critical_stock_items()
    dead_items = inventory_service.dead_stock_items()
    
    return render_template(
        "low_stock.html",
        low_stock_items=low_items,
        critical_stock_items=critical_items,
        dead_stock_items=dead_items
    )


# -----------------------
# DEAD STOCK PAGE
# -----------------------
@app.route("/dead-stock")
def dead_stock():
    items = inventory_service.dead_stock_items()
    return render_template("dead_stock.html", items=items)


# -----------------------
# UPLOAD SALES CSV
# -----------------------
@app.route("/upload-sales", methods=["GET", "POST"])
def upload_sales():
    if request.method == "GET":
        return render_template("upload.html")

    try:
        file = request.files.get("file")
        if not file:
            flash("✗ No file uploaded", "error")
            return redirect("/upload-sales")

        csv_text = file.stream.read().decode("utf-8")
        reader = csv.reader(io.StringIO(csv_text))

        csv_data = {}
        for row in reader:
            if len(row) >= 2:
                csv_data[row[0]] = int(row[1])

        updated_count = inventory_service.apply_sales_csv(csv_data)
        flash(f"✓ Successfully updated {updated_count} items from CSV", "success")
        
    except Exception as e:
        flash(f"✗ Error processing CSV: {str(e)}", "error")
        return redirect("/upload-sales")

    return redirect("/inventory")


# -----------------------
# DASHBOARD PAGE
# -----------------------
@app.route("/dashboard")
def dashboard():
    alerts = inventory_service.get_alerts()
    return render_template("dashboard.html", alerts=alerts)


# -----------------------
# DASHBOARD DATA API
# -----------------------
@app.route("/api/dashboard-data")
def dashboard_data():
    items = inventory_service.list_items()
    stats = inventory_service.get_dashboard_stats()

    # Sample sales trend data (replace with real data if available)
    sales_dates = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    sales_values = [120, 170, 90, 210, 300, 400, 320]

    # Stock levels - top 10 by stock quantity
    sorted_by_stock = sorted(items, key=lambda x: x.get("stock", 0), reverse=True)[:10]
    stock_names = [i["name"][:20] for i in sorted_by_stock]
    stock_values = [i["stock"] for i in sorted_by_stock]

    # Top selling products
    top_sorted = sorted(items, key=lambda x: x.get("daily_sales", 0), reverse=True)[:5]
    top_names = [i["name"][:20] for i in top_sorted]
    top_values = [i.get("daily_sales", 0) for i in top_sorted]

    # Category distribution
    category_labels = [cat.capitalize() for cat in stats["categories"].keys()]
    category_values = list(stats["categories"].values())

    return jsonify({
        "sales_dates": sales_dates,
        "sales_values": sales_values,
        "stock_names": stock_names,
        "stock_values": stock_values,
        "top_selling_names": top_names,
        "top_selling_values": top_values,
        "category_labels": category_labels,
        "category_values": category_values
    })


# -----------------------
# ALERTS API (for real-time notifications)
# -----------------------
@app.route("/api/alerts")
def get_alerts():
    alerts = inventory_service.get_alerts()
    return jsonify(alerts)


# -----------------------
# SEARCH (Frontend Only)
# -----------------------
@app.route("/search")
def search():
    return render_template("search.html")


# -----------------------
# RUN APP
# -----------------------
if __name__ == "__main__":
    app.run(debug=True)
