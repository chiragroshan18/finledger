import uuid
from datetime import datetime
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

transactions_by_id = {}
transactions_list = []

budgets_by_id = {}
budgets_list = []

goals_by_id = {}
goals_list = []

recurring_by_id = {}
recurring_list = []

def seed_data():
    seed_txns = [
        ("Income", 68500.0, "Salary", "Monthly Software Engineer Salary", "2026-09-01", "Bank Transfer", "Completed"),
        ("Income", 12500.0, "Freelance", "Web Design Consultation Project", "2026-09-05", "UPI", "Completed"),
        ("Income", 2400.0, "Interest", "Fixed Deposit Interest Payout", "2026-09-10", "Bank Transfer", "Completed"),
        ("Expense", 15000.0, "Rent", "Apartment Rent for September", "2026-09-02", "Bank Transfer", "Completed"),
        ("Expense", 6250.0, "Food", "Supermarket Groceries & Dining Out", "2026-09-06", "UPI", "Completed"),
        ("Expense", 2850.0, "Transport", "Monthly Metro Pass & Fuel refills", "2026-09-08", "UPI", "Completed"),
        ("Expense", 3400.0, "Bills", "Electricity & High-Speed Fiber Internet", "2026-09-10", "Card", "Completed"),
        ("Expense", 2100.0, "Shopping", "Autumn Apparel & Household Supplies", "2026-09-12", "Card", "Completed"),
        ("Expense", 1200.0, "Entertainment", "Movie Tickets & Streaming subscriptions", "2026-09-14", "UPI", "Completed"),
        ("Expense", 1800.0, "Health", "Pharmacy Prescription & Annual Checkup", "2026-09-18", "Cash", "Completed"),
        ("Expense", 950.0, "Education", "Technical E-Book & Online Course", "2026-09-20", "UPI", "Completed")
    ]
    
    for t_type, amt, cat, desc, dt, method, status in seed_txns:
        t_id = f"TXN-{uuid.uuid4().hex[:6].upper()}"
        item = {
            "id": t_id,
            "type": t_type,
            "amount": amt,
            "category": cat,
            "description": desc,
            "date": dt,
            "payment_method": method,
            "status": status,
            "created_at": datetime.now().isoformat()
        }
        transactions_by_id[t_id] = item
        transactions_list.append(item)

    seed_budgets = [
        ("Food", 8000.0),
        ("Transport", 4000.0),
        ("Shopping", 5000.0),
        ("Bills", 4500.0),
        ("Entertainment", 2500.0)
    ]
    for cat, amt in seed_budgets:
        b_id = f"BDG-{uuid.uuid4().hex[:6].upper()}"
        b_item = {
            "id": b_id,
            "category": cat,
            "amount": amt,
            "period": "Monthly"
        }
        budgets_by_id[b_id] = b_item
        budgets_list.append(b_item)

    seed_goals = [
        ("New Laptop", 80000.0, 42500.0, "2026-12-31", "Electronics"),
        ("Emergency Fund", 150000.0, 95000.0, "2027-03-31", "Savings"),
        ("Vacation Trip", 35000.0, 18000.0, "2026-11-15", "Travel")
    ]
    for name, target, saved, dt, cat in seed_goals:
        g_id = f"GOL-{uuid.uuid4().hex[:6].upper()}"
        g_item = {
            "id": g_id,
            "name": name,
            "target_amount": target,
            "saved_amount": saved,
            "target_date": dt,
            "category": cat
        }
        goals_by_id[g_id] = g_item
        goals_list.append(g_item)

    seed_recurring = [
        ("Apartment Rent", 15000.0, "Rent", "Monthly", "2026-10-01", "Bank Transfer"),
        ("High-Speed Fiber Internet", 1200.0, "Bills", "Monthly", "2026-10-05", "UPI"),
        ("Health Insurance Premium", 2400.0, "Health", "Monthly", "2026-10-10", "Card"),
        ("Streaming Subscription Bundle", 499.0, "Entertainment", "Monthly", "2026-10-15", "Card")
    ]
    for name, amt, cat, freq, n_dt, method in seed_recurring:
        r_id = f"REC-{uuid.uuid4().hex[:6].upper()}"
        r_item = {
            "id": r_id,
            "name": name,
            "amount": amt,
            "category": cat,
            "frequency": freq,
            "next_date": n_dt,
            "payment_method": method
        }
        recurring_by_id[r_id] = r_item
        recurring_list.append(r_item)

seed_data()

def find_transaction(txn_id):
    return transactions_by_id.get(txn_id)

def find_budget(budget_id):
    return budgets_by_id.get(budget_id)

def find_goal(goal_id):
    return goals_by_id.get(goal_id)

def find_recurring_payment(payment_id):
    return recurring_by_id.get(payment_id)

def success_response(data, status_code=200):
    return jsonify({"success": True, "data": data}), status_code

def error_response(message, status_code=400):
    return jsonify({"success": False, "error": message}), status_code

def calculate_balance():
    inc = sum(t["amount"] for t in transactions_list if t["type"] == "Income")
    exp = sum(t["amount"] for t in transactions_list if t["type"] == "Expense")
    return round(inc - exp, 2), round(inc, 2), round(exp, 2)

def calculate_savings_rate(income, expenses):
    if income <= 0:
        return 0.0
    rate = ((income - expenses) / income) * 100
    return max(0.0, round(rate, 1))

def calculate_category_breakdown():
    cat_totals = {}
    exp_txns = [t for t in transactions_list if t["type"] == "Expense"]
    total_exp = sum(t["amount"] for t in exp_txns)
    
    for t in exp_txns:
        c = t["category"]
        cat_totals[c] = cat_totals.get(c, 0.0) + t["amount"]
        
    breakdown = []
    for cat, amt in cat_totals.items():
        pct = round((amt / total_exp) * 100, 1) if total_exp > 0 else 0.0
        breakdown.append({
            "category": cat,
            "amount": round(amt, 2),
            "percentage": pct
        })
        
    breakdown.sort(key=lambda x: x["amount"], reverse=True)
    return breakdown, round(total_exp, 2)

def calculate_budget_usage():
    cat_expenses = {}
    for t in transactions_list:
        if t["type"] == "Expense":
            c = t["category"]
            cat_expenses[c] = cat_expenses.get(c, 0.0) + t["amount"]
            
    usage_list = []
    for b in budgets_list:
        spent = cat_expenses.get(b["category"], 0.0)
        rem = b["amount"] - spent
        pct = round((spent / b["amount"]) * 100, 1) if b["amount"] > 0 else 0.0
        
        status = "Healthy"
        if pct > 100:
            status = "Exceeded"
        elif pct >= 85:
            status = "Near Limit"
        elif pct >= 70:
            status = "Approaching Limit"
            
        usage_list.append({
            "id": b["id"],
            "category": b["category"],
            "budget_amount": b["amount"],
            "spent": round(spent, 2),
            "remaining": round(rem, 2),
            "percentage": pct,
            "status": status
        })
    return usage_list

def calculate_goal_progress(goal):
    target = goal["target_amount"]
    saved = goal["saved_amount"]
    pct = round((saved / target) * 100, 1) if target > 0 else 0.0
    return {
        "id": goal["id"],
        "name": goal["name"],
        "target_amount": target,
        "saved_amount": saved,
        "remaining": max(0.0, round(target - saved, 2)),
        "target_date": goal["target_date"],
        "category": goal.get("category", "General"),
        "percentage": min(100.0, pct)
    }

def build_notifications():
    notifs = []
    budget_usage = calculate_budget_usage()
    for bu in budget_usage:
        if bu["status"] == "Exceeded":
            notifs.append({
                "id": f"notif-{bu['id']}",
                "type": "danger",
                "title": "Budget Exceeded",
                "message": f"Your {bu['category']} budget has exceeded the limit by ₹{abs(bu['remaining']):,.2f}.",
                "timestamp": "Just now"
            })
        elif bu["status"] in ["Near Limit", "Approaching Limit"]:
            notifs.append({
                "id": f"notif-{bu['id']}",
                "type": "warning",
                "title": "Budget Alert",
                "message": f"Your {bu['category']} budget is at {bu['percentage']}% usage.",
                "timestamp": "Today"
            })
            
    for g in goals_list:
        prog = calculate_goal_progress(g)
        if prog["percentage"] >= 50 and prog["percentage"] < 100:
            notifs.append({
                "id": f"notif-{g['id']}",
                "type": "info",
                "title": "Goal Milestone",
                "message": f"Goal '{g['name']}' has reached {prog['percentage']}% progress!",
                "timestamp": "Recent"
            })
            
    for r in recurring_list[:2]:
        notifs.append({
            "id": f"notif-{r['id']}",
            "type": "info",
            "title": "Upcoming Payment",
            "message": f"{r['name']} of ₹{r['amount']:,.2f} due on {r['next_date']}.",
            "timestamp": "Upcoming"
        })
        
    return notifs

def build_insights():
    insights = []
    breakdown, total_exp = calculate_category_breakdown()
    bal, inc, exp = calculate_balance()
    s_rate = calculate_savings_rate(inc, exp)
    b_usage = calculate_budget_usage()
    
    if breakdown:
        top_cat = breakdown[0]
        insights.append(f"{top_cat['category']} is currently your highest spending category ({top_cat['percentage']}% of expenses).")
        
    exceeded = [b for b in b_usage if b["status"] == "Exceeded"]
    if exceeded:
        insights.append(f"{exceeded[0]['category']} budget has exceeded its monthly limit.")
    else:
        avg_u = round(sum(b["percentage"] for b in b_usage) / len(b_usage), 1) if b_usage else 0
        insights.append(f"You have used an average of {avg_u}% of your planned category budgets.")
        
    insights.append(f"Your current calculated savings rate is {s_rate}%.")
    insights.append(f"You have {len(recurring_list)} scheduled recurring commitments.")
    return insights

def build_dashboard():
    bal, inc, exp = calculate_balance()
    s_rate = calculate_savings_rate(inc, exp)
    breakdown, _ = calculate_category_breakdown()
    b_usage = calculate_budget_usage()
    g_progs = [calculate_goal_progress(g) for g in goals_list]
    
    recent_txns = sorted(transactions_list, key=lambda x: x["date"], reverse=True)[:5]
    upcoming_rec = sorted(recurring_list, key=lambda x: x["next_date"])[:3]
    
    monthly_cash_flow = [
        {"month": "May", "income": 62000, "expenses": 24000, "net": 38000},
        {"month": "Jun", "income": 65000, "expenses": 26500, "net": 38500},
        {"month": "Jul", "income": 64000, "expenses": 25000, "net": 39000},
        {"month": "Aug", "income": 67000, "expenses": 28000, "net": 39000},
        {"month": "Sep", "income": inc, "expenses": exp, "net": bal}
    ]
    
    return {
        "balance": bal,
        "total_income": inc,
        "total_expenses": exp,
        "savings_rate": s_rate,
        "category_breakdown": breakdown,
        "budget_usage": b_usage,
        "goals": g_progs,
        "recent_transactions": recent_txns,
        "upcoming_recurring": upcoming_rec,
        "cash_flow": monthly_cash_flow,
        "insights": build_insights(),
        "notifications": build_notifications()
    }

def validate_transaction(data):
    if not isinstance(data, dict):
        return False, "Payload must be a JSON object."
    t_type = data.get("type")
    if t_type not in ["Income", "Expense"]:
        return False, "Transaction type must be 'Income' or 'Expense'."
    try:
        amt = float(data.get("amount", 0))
        if amt <= 0:
            return False, "Amount must be a positive number greater than 0."
    except (ValueError, TypeError):
        return False, "Invalid amount value."
    if not data.get("category") or not isinstance(data.get("category"), str):
        return False, "Category is required."
    if not data.get("description") or not isinstance(data.get("description"), str):
        return False, "Description is required."
    if not data.get("date") or not isinstance(data.get("date"), str):
        return False, "Date is required."
    return True, None

def validate_budget(data):
    if not isinstance(data, dict):
        return False, "Payload must be a JSON object."
    if not data.get("category"):
        return False, "Category is required."
    try:
        amt = float(data.get("amount", 0))
        if amt <= 0:
            return False, "Budget amount must be greater than 0."
    except (ValueError, TypeError):
        return False, "Invalid budget amount."
    return True, None

def validate_goal(data):
    if not isinstance(data, dict):
        return False, "Payload must be a JSON object."
    if not data.get("name"):
        return False, "Goal name is required."
    try:
        target = float(data.get("target_amount", 0))
        if target <= 0:
            return False, "Target amount must be greater than 0."
    except (ValueError, TypeError):
        return False, "Invalid target amount."
    return True, None

def validate_recurring(data):
    if not isinstance(data, dict):
        return False, "Payload must be a JSON object."
    if not data.get("name"):
        return False, "Payment name is required."
    try:
        amt = float(data.get("amount", 0))
        if amt <= 0:
            return False, "Amount must be greater than 0."
    except (ValueError, TypeError):
        return False, "Invalid amount."
    return True, None

@app.route("/api/dashboard", methods=["GET"])
def api_get_dashboard():
    return success_response(build_dashboard())

@app.route("/api/transactions", methods=["GET"])
def api_get_transactions():
    search = request.args.get("search", "").lower().strip()
    t_type = request.args.get("type", "all")
    category = request.args.get("category", "all")
    method = request.args.get("payment_method", "all")
    sort_by = request.args.get("sort_by", "newest")

    filtered = list(transactions_list)

    if t_type != "all":
        filtered = [t for t in filtered if t["type"].lower() == t_type.lower()]
    if category != "all":
        filtered = [t for t in filtered if t["category"].lower() == category.lower()]
    if method != "all":
        filtered = [t for t in filtered if t["payment_method"].lower() == method.lower()]
    if search:
        filtered = [t for t in filtered if search in t["description"].lower() or search in t["category"].lower() or search in t["id"].lower()]

    if sort_by == "oldest":
        filtered.sort(key=lambda x: x["date"])
    elif sort_by == "highest":
        filtered.sort(key=lambda x: x["amount"], reverse=True)
    elif sort_by == "lowest":
        filtered.sort(key=lambda x: x["amount"])
    else:
        filtered.sort(key=lambda x: x["date"], reverse=True)

    return success_response(filtered)

@app.route("/api/transactions/<txn_id>", methods=["GET"])
def api_get_transaction(txn_id):
    txn = find_transaction(txn_id)
    if not txn:
        return error_response("Transaction not found.", 404)
    return success_response(txn)

@app.route("/api/transactions", methods=["POST"])
def api_create_transaction():
    data = request.get_json(silent=True)
    is_valid, err = validate_transaction(data)
    if not is_valid:
        return error_response(err, 400)

    t_id = f"TXN-{uuid.uuid4().hex[:6].upper()}"
    new_txn = {
        "id": t_id,
        "type": data["type"],
        "amount": round(float(data["amount"]), 2),
        "category": data["category"],
        "description": data["description"].strip(),
        "date": data["date"],
        "payment_method": data.get("payment_method", "UPI"),
        "status": data.get("status", "Completed"),
        "created_at": datetime.now().isoformat()
    }

    transactions_by_id[t_id] = new_txn
    transactions_list.append(new_txn)
    return success_response(new_txn, 201)

@app.route("/api/transactions/<txn_id>", methods=["PATCH"])
def api_update_transaction(txn_id):
    txn = find_transaction(txn_id)
    if not txn:
        return error_response("Transaction not found.", 404)

    data = request.get_json(silent=True) or {}
    if "amount" in data:
        try:
            amt = float(data["amount"])
            if amt <= 0:
                return error_response("Amount must be greater than 0.")
            txn["amount"] = round(amt, 2)
        except (ValueError, TypeError):
            return error_response("Invalid amount.")

    if "type" in data and data["type"] in ["Income", "Expense"]:
        txn["type"] = data["type"]
    if "category" in data:
        txn["category"] = data["category"]
    if "description" in data:
        txn["description"] = data["description"]
    if "date" in data:
        txn["date"] = data["date"]
    if "payment_method" in data:
        txn["payment_method"] = data["payment_method"]

    return success_response(txn)

@app.route("/api/transactions/<txn_id>", methods=["DELETE"])
def api_delete_transaction(txn_id):
    txn = find_transaction(txn_id)
    if not txn:
        return error_response("Transaction not found.", 404)

    transactions_list.remove(txn)
    del transactions_by_id[txn_id]
    return success_response({"id": txn_id, "deleted": True})

@app.route("/api/budgets", methods=["GET"])
def api_get_budgets():
    usage = calculate_budget_usage()
    return success_response(usage)

@app.route("/api/budgets", methods=["POST"])
def api_create_budget():
    data = request.get_json(silent=True)
    is_valid, err = validate_budget(data)
    if not is_valid:
        return error_response(err, 400)

    b_id = f"BDG-{uuid.uuid4().hex[:6].upper()}"
    new_b = {
        "id": b_id,
        "category": data["category"],
        "amount": round(float(data["amount"]), 2),
        "period": "Monthly"
    }

    budgets_by_id[b_id] = new_b
    budgets_list.append(new_b)
    return success_response(new_b, 201)

@app.route("/api/budgets/<budget_id>", methods=["PATCH"])
def api_update_budget(budget_id):
    b = find_budget(budget_id)
    if not b:
        return error_response("Budget not found.", 404)

    data = request.get_json(silent=True) or {}
    if "amount" in data:
        try:
            amt = float(data["amount"])
            if amt <= 0:
                return error_response("Amount must be greater than 0.")
            b["amount"] = round(amt, 2)
        except (ValueError, TypeError):
            return error_response("Invalid amount.")

    if "category" in data:
        b["category"] = data["category"]

    return success_response(b)

@app.route("/api/budgets/<budget_id>", methods=["DELETE"])
def api_delete_budget(budget_id):
    b = find_budget(budget_id)
    if not b:
        return error_response("Budget not found.", 404)

    budgets_list.remove(b)
    del budgets_by_id[budget_id]
    return success_response({"id": budget_id, "deleted": True})

@app.route("/api/goals", methods=["GET"])
def api_get_goals():
    progs = [calculate_goal_progress(g) for g in goals_list]
    return success_response(progs)

@app.route("/api/goals", methods=["POST"])
def api_create_goal():
    data = request.get_json(silent=True)
    is_valid, err = validate_goal(data)
    if not is_valid:
        return error_response(err, 400)

    g_id = f"GOL-{uuid.uuid4().hex[:6].upper()}"
    saved = round(float(data.get("saved_amount", 0)), 2)
    new_g = {
        "id": g_id,
        "name": data["name"],
        "target_amount": round(float(data["target_amount"]), 2),
        "saved_amount": saved,
        "target_date": data.get("target_date", "2026-12-31"),
        "category": data.get("category", "General")
    }

    goals_by_id[g_id] = new_g
    goals_list.append(new_g)
    return success_response(calculate_goal_progress(new_g), 201)

@app.route("/api/goals/<goal_id>", methods=["PATCH"])
def api_update_goal(goal_id):
    g = find_goal(goal_id)
    if not g:
        return error_response("Goal not found.", 404)

    data = request.get_json(silent=True) or {}
    if "name" in data:
        g["name"] = data["name"]
    if "target_amount" in data:
        try:
            g["target_amount"] = round(float(data["target_amount"]), 2)
        except (ValueError, TypeError):
            pass
    if "saved_amount" in data:
        try:
            g["saved_amount"] = round(float(data["saved_amount"]), 2)
        except (ValueError, TypeError):
            pass
    if "target_date" in data:
        g["target_date"] = data["target_date"]

    return success_response(calculate_goal_progress(g))

@app.route("/api/goals/<goal_id>/contribute", methods=["POST"])
def api_contribute_goal(goal_id):
    g = find_goal(goal_id)
    if not g:
        return error_response("Goal not found.", 404)

    data = request.get_json(silent=True) or {}
    try:
        contrib = float(data.get("amount", 0))
        if contrib <= 0:
            return error_response("Contribution amount must be greater than 0.")
    except (ValueError, TypeError):
        return error_response("Invalid contribution amount.")

    g["saved_amount"] = round(g["saved_amount"] + contrib, 2)
    return success_response(calculate_goal_progress(g))

@app.route("/api/goals/<goal_id>", methods=["DELETE"])
def api_delete_goal(goal_id):
    g = find_goal(goal_id)
    if not g:
        return error_response("Goal not found.", 404)

    goals_list.remove(g)
    del goals_by_id[goal_id]
    return success_response({"id": goal_id, "deleted": True})

@app.route("/api/recurring", methods=["GET"])
def api_get_recurring():
    return success_response(recurring_list)

@app.route("/api/recurring", methods=["POST"])
def api_create_recurring():
    data = request.get_json(silent=True)
    is_valid, err = validate_recurring(data)
    if not is_valid:
        return error_response(err, 400)

    r_id = f"REC-{uuid.uuid4().hex[:6].upper()}"
    new_r = {
        "id": r_id,
        "name": data["name"],
        "amount": round(float(data["amount"]), 2),
        "category": data.get("category", "Bills"),
        "frequency": data.get("frequency", "Monthly"),
        "next_date": data.get("next_date", "2026-10-01"),
        "payment_method": data.get("payment_method", "Bank Transfer")
    }

    recurring_by_id[r_id] = new_r
    recurring_list.append(new_r)
    return success_response(new_r, 201)

@app.route("/api/recurring/<payment_id>", methods=["DELETE"])
def api_delete_recurring(payment_id):
    r = find_recurring_payment(payment_id)
    if not r:
        return error_response("Recurring payment not found.", 404)

    recurring_list.remove(r)
    del recurring_by_id[payment_id]
    return success_response({"id": payment_id, "deleted": True})

@app.route("/api/analytics", methods=["GET"])
def api_get_analytics():
    bal, inc, exp = calculate_balance()
    s_rate = calculate_savings_rate(inc, exp)
    breakdown, _ = calculate_category_breakdown()
    b_usage = calculate_budget_usage()

    pm_totals = {}
    for t in transactions_list:
        m = t.get("payment_method", "Other")
        pm_totals[m] = pm_totals.get(m, 0.0) + t["amount"]

    pm_breakdown = [{"method": k, "amount": round(v, 2)} for k, v in pm_totals.items()]

    return success_response({
        "balance": bal,
        "total_income": inc,
        "total_expenses": exp,
        "savings_rate": s_rate,
        "category_breakdown": breakdown,
        "budget_usage": b_usage,
        "payment_methods": pm_breakdown,
        "insights": build_insights()
    })

@app.route("/api/notifications", methods=["GET"])
def api_get_notifications():
    return success_response(build_notifications())

@app.route("/api/search", methods=["GET"])
def api_global_search():
    q = request.args.get("q", "").lower().strip()
    if not q:
        return success_response({"transactions": [], "budgets": [], "goals": [], "recurring": []})

    matched_txns = [t for t in transactions_list if q in t["description"].lower() or q in t["category"].lower() or q in t["id"].lower()]
    matched_bdg = [b for b in budgets_list if q in b["category"].lower() or q in b["id"].lower()]
    matched_goals = [g for g in goals_list if q in g["name"].lower() or q in g["category"].lower() or q in g["id"].lower()]
    matched_rec = [r for r in recurring_list if q in r["name"].lower() or q in r["category"].lower() or q in r["id"].lower()]

    return success_response({
        "transactions": matched_txns[:5],
        "budgets": matched_bdg[:5],
        "goals": matched_goals[:5],
        "recurring": matched_rec[:5]
    })

@app.route("/api/reports", methods=["GET"])
def api_get_reports():
    bal, inc, exp = calculate_balance()
    breakdown, _ = calculate_category_breakdown()
    b_usage = calculate_budget_usage()
    
    return success_response({
        "title": "FinLedger Comprehensive Executive Financial Report",
        "date_generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total_income": inc,
        "total_expenses": exp,
        "net_savings": bal,
        "savings_rate": calculate_savings_rate(inc, exp),
        "transaction_count": len(transactions_list),
        "category_breakdown": breakdown,
        "budget_performance": b_usage
    })

@app.route("/")
def page_index():
    return render_template("index.html")

@app.route("/transactions")
def page_transactions():
    return render_template("transactions.html")

@app.route("/budgets")
def page_budgets():
    return render_template("budgets.html")

@app.route("/goals")
def page_goals():
    return render_template("goals.html")

@app.route("/analytics")
def page_analytics():
    return render_template("analytics.html")

@app.route("/reports")
def page_reports():
    return render_template("reports.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
