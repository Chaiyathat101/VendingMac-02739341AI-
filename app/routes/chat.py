from fastapi import APIRouter
from pydantic import BaseModel

from app.services.product_service import get_all_products

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    message: str


def _search_product(name: str, products: list) -> list:
    """ค้นหาสินค้าจากชื่อ (fuzzy)"""
    name_lower = name.lower()
    return [p for p in products if name_lower in p["name"].lower()]


def _get_bot_reply(msg: str, products: list) -> dict:
    """rule-based logic คืน {text, quick_replies?}"""
    m = msg.strip().lower()

    # ทักทาย
    if any(w in m for w in ["สวัสดี", "หวัดดี", "hello", "hi", "ดีจ้า", "ดีครับ"]):
        return {
            "text": "สวัสดีครับ! 👋 ผมคือ VendBot ผู้ช่วยตู้เครื่องเขียนอัตโนมัติ\nจะให้ช่วยอะไรดีครับ?",
            "quick_replies": ["สินค้ามีอะไรบ้าง", "วิธีชำระเงิน", "ติดต่อเจ้าหน้าที่"]
        }

    # สินค้าทั้งหมด
    if any(w in m for w in ["สินค้า", "มีอะไร", "ขายอะไร", "รายการ"]):
        available = [p for p in products if p.get("status") != "inactive" and p.get("stock", 0) > 0]
        if not available:
            return {"text": "ขณะนี้ยังไม่มีสินค้าในระบบครับ"}
        # จัดกลุ่มตาม category
        cats: dict = {}
        for p in available[:20]:
            cat = p.get("category", "อื่นๆ")
            cats.setdefault(cat, []).append(p["name"])
        lines = ["📦 สินค้าที่มีในตู้ตอนนี้:\n"]
        for cat, names in cats.items():
            lines.append(f"**{cat}**: {', '.join(names)}")
        return {
            "text": "\n".join(lines),
            "quick_replies": ["ราคาปากกา", "ราคาสมุด", "วิธีชำระเงิน"]
        }

    # ราคา / stock สินค้าเฉพาะ
    if any(w in m for w in ["ราคา", "เท่าไหร่", "เท่าไร", "บาท", "กี่บาท"]):
        # ตัดคำว่า "ราคา" ออกแล้วค้นหา
        query = m.replace("ราคา", "").replace("เท่าไหร่", "").replace("เท่าไร", "").replace("กี่บาท", "").strip()
        found = _search_product(query, products) if query else []
        if found:
            lines = ["💰 ราคาสินค้าที่พบ:\n"]
            for p in found[:5]:
                stock_txt = f"(เหลือ {p['stock']} ชิ้น)" if p.get("stock", 0) > 0 else "❌ หมดแล้ว"
                lines.append(f"• {p['name']}: **{p['price']} บาท** {stock_txt}")
            return {"text": "\n".join(lines), "quick_replies": ["วิธีชำระเงิน", "สินค้ามีอะไรบ้าง"]}
        # ไม่ระบุชื่อ → แสดงถูกสุด 5 อันดับ
        sorted_p = sorted([p for p in products if p.get("stock", 0) > 0], key=lambda x: x["price"])[:5]
        if sorted_p:
            lines = ["💰 สินค้าราคาย่อมเยาว์:\n"]
            for p in sorted_p:
                lines.append(f"• {p['name']}: {p['price']} บาท")
            return {"text": "\n".join(lines), "quick_replies": ["สินค้ามีอะไรบ้าง", "วิธีชำระเงิน"]}
        return {"text": "ลองระบุชื่อสินค้าด้วยนะครับ เช่น 'ราคาปากกา'"}

    # ค้นหาสินค้าโดยตรง
    found = _search_product(m, products)
    if found and any(w in m for w in ["หา", "มี", "ขาย", found[0]["name"].lower()[:3]]):
        lines = [f"🔍 ผลการค้นหา '{msg}':\n"]
        for p in found[:4]:
            status = "✅ มีสินค้า" if p.get("stock", 0) > 0 else "❌ หมดแล้ว"
            lines.append(f"• {p['name']}: {p['price']} บาท — {status}")
        return {"text": "\n".join(lines), "quick_replies": ["วิธีชำระเงิน"]}

    # วิธีชำระเงิน
    if any(w in m for w in ["ชำระ", "จ่าย", "payment", "qr", "เงินสด", "โอน", "สแกน"]):
        return {
            "text": "💳 วิธีชำระเงินมี 2 แบบ:\n\n**1. เงินสด** 💵\n→ หยอดเงินที่ตู้ได้เลยครับ\n\n**2. QR Code** 📱\n→ สแกน PromptPay ผ่าน app ธนาคารใดก็ได้\n→ กด 'ชำระเงิน' ในตะกร้าแล้วเลือก QR Code",
            "quick_replies": ["สินค้ามีอะไรบ้าง", "ติดต่อเจ้าหน้าที่"]
        }

    # stock / ของหมด
    if any(w in m for w in ["หมด", "stock", "เหลือ", "stock"]):
        out = [p for p in products if p.get("stock", 0) == 0]
        low = [p for p in products if 0 < p.get("stock", 0) <= p.get("low_stock_threshold", 5)]
        lines = []
        if out:
            lines.append(f"❌ สินค้าหมด ({len(out)} รายการ): " + ", ".join(p["name"] for p in out[:5]))
        if low:
            lines.append(f"⚠️ ใกล้หมด ({len(low)} รายการ): " + ", ".join(p["name"] for p in low[:5]))
        if not lines:
            lines.append("✅ สินค้าทุกรายการยังมีพร้อมครับ!")
        return {"text": "\n".join(lines), "quick_replies": ["สินค้ามีอะไรบ้าง"]}

    # ติดต่อ
    if any(w in m for w in ["ติดต่อ", "โทร", "เบอร์", "line", "email", "อีเมล", "เจ้าหน้าที่"]):
        return {
            "text": "📞 ช่องทางติดต่อ:\n\n📱 โทร: 02-XXX-XXXX\n📧 Email: support@vendingmac.com\n💬 LINE: @vendingmac\n🕐 จ-ศ 08:00–17:00 น.",
            "quick_replies": ["สินค้ามีอะไรบ้าง", "วิธีชำระเงิน"]
        }

    # ขอบคุณ
    if any(w in m for w in ["ขอบคุณ", "thank", "ขอบใจ", "โอเค", "ok", "เข้าใจ"]):
        return {
            "text": "ยินดีให้บริการครับ 😊 มีอะไรอีกไหมครับ?",
            "quick_replies": ["สินค้ามีอะไรบ้าง", "ราคาสินค้า", "วิธีชำระเงิน"]
        }

    # default
    return {
        "text": f"ขออภัยครับ ไม่เข้าใจคำถามนี้ 🤔\nลองถามเกี่ยวกับ:",
        "quick_replies": ["สินค้ามีอะไรบ้าง", "ราคาสินค้า", "วิธีชำระเงิน", "ติดต่อเจ้าหน้าที่"]
    }


@router.post("")
def chat(body: ChatMessage):
    products = get_all_products()
    return _get_bot_reply(body.message, products)
