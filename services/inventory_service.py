from config import LOW_STOCK_LIMIT, DEAD_STOCK_LIMIT, CRITICAL_STOCK_LIMIT
from services.algolia_service import AlgoliaService

algolia = AlgoliaService()

class InventoryService:

    def list_items(self):
        return algolia.get_all_items()

    def get_item(self, object_id):
        return algolia.get_item(object_id)

    def add_item(self, form):
        new_item = {
            "objectID": form.get("objectID"),
            "name": form.get("name"),
            "brand": form.get("brand"),
            "category": form.get("category"),
            "price": float(form.get("price", 0)),
            "stock": int(form.get("stock", 0)),
            "daily_sales": int(form.get("daily_sales", 0)),
            "supplier": form.get("supplier", ""),
            "image": form.get("image", ""),
            "description": form.get("description", "")
        }
        algolia.add_item(new_item)

    def update_item(self, object_id, form):
        fields = {
            "name": form.get("name"),
            "brand": form.get("brand"),
            "category": form.get("category"),
            "price": float(form.get("price", 0)),
            "stock": int(form.get("stock", 0)),
            "daily_sales": int(form.get("daily_sales", 0)),
            "supplier": form.get("supplier", ""),
            "image": form.get("image", ""),
            "description": form.get("description", "")
        }
        algolia.update_item(object_id, fields)

    def delete_item(self, object_id):
        algolia.delete_item(object_id)

    def low_stock_items(self):
        """Get items with stock below LOW_STOCK_LIMIT but not dead stock"""
        items = self.list_items()
        return [i for i in items if DEAD_STOCK_LIMIT < i.get("stock", 0) < LOW_STOCK_LIMIT]

    def dead_stock_items(self):
        """Get items with 0 stock"""
        items = self.list_items()
        return [i for i in items if i.get("stock", 0) == DEAD_STOCK_LIMIT]
    
    def critical_stock_items(self):
        """Get items with stock below CRITICAL_STOCK_LIMIT"""
        items = self.list_items()
        return [i for i in items if DEAD_STOCK_LIMIT < i.get("stock", 0) < CRITICAL_STOCK_LIMIT]

    def get_alerts(self):
        """Get all alerts for dashboard"""
        items = self.list_items()
        
        dead_stock = [i for i in items if i.get("stock", 0) == DEAD_STOCK_LIMIT]
        critical_stock = [i for i in items if DEAD_STOCK_LIMIT < i.get("stock", 0) < CRITICAL_STOCK_LIMIT]
        low_stock = [i for i in items if CRITICAL_STOCK_LIMIT <= i.get("stock", 0) < LOW_STOCK_LIMIT]
        
        return {
            "dead_stock": dead_stock,
            "critical_stock": critical_stock,
            "low_stock": low_stock,
            "total_alerts": len(dead_stock) + len(critical_stock) + len(low_stock)
        }

    def get_dashboard_stats(self):
        """Get comprehensive dashboard statistics"""
        items = self.list_items()
        
        total_items = len(items)
        total_stock_value = sum(i.get("price", 0) * i.get("stock", 0) for i in items)
        total_sales = sum(i.get("daily_sales", 0) for i in items)
        
        # Category distribution
        categories = {}
        for item in items:
            cat = item.get("category", "other")
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            "total_items": total_items,
            "total_stock_value": total_stock_value,
            "total_sales": total_sales,
            "categories": categories
        }

    def apply_sales_csv(self, csv_data):
        updates = []

        for item_id, qty in csv_data.items():
            item = algolia.get_item(item_id)
            if not item:
                continue

            new_stock = max(item.get("stock", 0) - qty, 0)
            
            updates.append({
                "objectID": item_id,
                "stock": new_stock,
                "daily_sales": item.get("daily_sales", 0) + qty
            })

        if updates:
            algolia.bulk_update(updates)
        
        return len(updates)

inventory_service = InventoryService()
