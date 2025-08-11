from database import Database

def delete_щелкунчик():
    db = Database()
    
    # Удаляем пост с ID 13 (который содержит "Щелкунчик")
    deleted = db.delete_content_by_id(13)
    
    if deleted:
        print("✅ Пост с 'Щелкунчик' (ID: 13) успешно удалён из базы данных!")
    else:
        print("❌ Пост с ID 13 не найден в базе данных.")

if __name__ == "__main__":
    delete_щелкунчик() 