# solid-octo-eureka

To set up your development environment for this Django project, follow these steps:

---

## 1. **Install Python**
Make sure you have Python 3.8+ installed.  
You can check with:
```sh
python3 --version
```

---

## 2. **Create a Virtual Environment**
This keeps dependencies isolated.
```sh
python -m venv venv
```
Activate it:
- **Windows:**
  ```sh
  venv\Scripts\activate
  ```
- **macOS/Linux:**
  ```sh
  source venv/bin/activate
  ```

---

## 3. **Install Django and Other Dependencies**
If you have a `requirements.txt`, run:
```sh
pip install -r requirements.txt
```
If not, install Django and Pillow (for image fields):
```sh
pip install django pillow
```