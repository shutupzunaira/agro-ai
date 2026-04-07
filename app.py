"""
app.py — Entry point for AgriSense
"""

from flask import Flask
from extensions import db, login_manager

from routes.pages import pages_bp
from routes.auth import auth_bp
from routes.ai_routes import ai_bp
from routes.blog import blog_bp
from routes.dashboard import dashboard_bp

import os


def create_app():
    app = Flask(__name__)

    # ── Config ─────────────────────────────
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "dev-secret-change-me-123"
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///agri.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["UPLOAD_FOLDER"] = os.path.join(
        app.root_path, "static", "uploads"
    )
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

    # ── Extensions ─────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # ── Blueprints ─────────────────────────
    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(ai_bp, url_prefix="/ai")
    app.register_blueprint(blog_bp, url_prefix="/blog")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")

    # ── DB Init ────────────────────────────
    with app.app_context():
        db.create_all()
        _seed_demo_data()

    return app


def _seed_demo_data():
    from models import BlogPost
    from extensions import db

    if BlogPost.query.count() == 0:
        demo = [
            BlogPost(
                title="How AI is changing crop yield prediction",
                slug="ai-crop-yield-prediction",
                summary="Machine learning models are helping farmers forecast harvests more accurately than ever before.",
                body="""
                <p>For centuries, predicting crop yields relied on instinct, experience, and a bit of luck.
                Today, machine learning algorithms can process satellite imagery, soil sensor data, and
                historical weather patterns to deliver forecasts that rival — and often surpass — expert agronomists.</p>

                <h2>Why accuracy matters</h2>
                <p>Yield prediction isn't just an academic exercise. Accurate forecasts help farmers decide
                how much to invest in fertiliser, when to harvest, and how to negotiate contracts with buyers.
                Overestimating can lead to wasted inputs; underestimating means lost revenue.</p>

                <h2>The role of Random Forests</h2>
                <p>Random Forest models are one of the most popular approaches. They work by building hundreds
                of decision trees, each trained on a random subset of the data, and averaging their predictions.
                This makes them resistant to overfitting and surprisingly accurate with tabular agricultural data.</p>

                <h2>Real-world results</h2>
                <p>In trials across India's rice belt, Random Forest models achieved 92% accuracy in predicting
                whether a field would produce above- or below-average yields, using just seven input variables:
                nitrogen, phosphorus, potassium, temperature, humidity, pH, and rainfall.</p>
                """,
                tag="Technology",
            ),
            BlogPost(
                title="Understanding soil health: a beginner's guide",
                slug="soil-health-beginners-guide",
                summary="Healthy soil is the foundation of productive farming. Learn the key indicators every farmer should monitor.",
                body="""
                <p>Soil isn't just dirt — it's a living ecosystem teeming with bacteria, fungi, earthworms,
                and organic matter. Understanding your soil is the single most impactful thing you can do
                to improve crop quality and long-term land productivity.</p>

                <h2>The big three: N-P-K</h2>
                <p><strong>Nitrogen (N)</strong> fuels leafy growth. <strong>Phosphorus (P)</strong> supports
                root development and flowering. <strong>Potassium (K)</strong> strengthens disease resistance
                and water regulation. Testing your soil for these macronutrients is the first step.</p>

                <h2>Why pH matters</h2>
                <p>Soil pH controls how available nutrients are to plant roots. Most crops thrive between
                pH 6.0 and 7.0. Acidic soils (below 5.5) lock up phosphorus and calcium; alkaline soils
                (above 8.0) can cause iron and manganese deficiencies.</p>

                <h2>How to test</h2>
                <p>You can use inexpensive home test kits, or send samples to a laboratory for detailed
                analysis. AgriSense's dashboard lets you log and track your readings over time, so you can
                spot trends before they become problems.</p>
                """,
                tag="Soil Science",
            ),
            BlogPost(
                title="Weed vs crop: how CNNs tell the difference",
                slug="weed-detection-cnn",
                summary="Convolutional neural networks can distinguish weeds from crops in field photos with over 95% accuracy.",
                body="""
                <p>Manual weeding is one of the most labour-intensive tasks in farming. What if a camera
                could do the spotting for you? That's exactly what convolutional neural networks (CNNs)
                are designed to do.</p>

                <h2>How a CNN sees an image</h2>
                <p>A CNN breaks an image into small patches and learns to recognise patterns — edges, textures,
                shapes — through layers of filters. Early layers detect simple features like leaf edges;
                deeper layers combine them into complex concepts like "broad-leaf weed" or "cereal crop."</p>

                <h2>Training the model</h2>
                <p>We trained our weed/crop classifier on thousands of labelled field images, resized to
                128×128 pixels. The model uses binary cross-entropy loss and a sigmoid output:
                if the probability exceeds 0.5, it classifies the image as "weed," otherwise "crop."</p>

                <h2>Practical use</h2>
                <p>Farmers can snap a photo in the field and get an instant classification. High-confidence
                weed detections trigger an alert to remove weeds immediately, while lower-confidence results
                suggest monitoring.</p>
                """,
                tag="Technology",
            ),
            BlogPost(
                title="Organic farming: myths vs facts",
                slug="organic-farming-myths-facts",
                summary="Separating common misconceptions from scientific evidence about organic agriculture.",
                body="""
                <p>Organic farming has exploded in popularity, but it's surrounded by strong opinions on
                both sides. Let's look at what the science actually says.</p>

                <h2>Myth: organic yields are always lower</h2>
                <p><strong>Fact:</strong> While organic yields are typically 10–20% lower for commodity crops,
                the gap narrows significantly for fruits, vegetables, and legumes. Some organic systems
                even match conventional yields after 3–5 years of soil building.</p>

                <h2>Myth: organic means no pesticides</h2>
                <p><strong>Fact:</strong> Organic farms can use approved pesticides — copper sulphate,
                neem oil, and pyrethrin, for example. The key difference is that synthetic chemicals are
                prohibited, not all pest management.</p>

                <h2>The real benefit</h2>
                <p>The strongest scientific case for organic farming is soil health. Long-term studies show
                organic fields have higher microbial diversity, better water retention, and more stable
                carbon storage than conventionally managed land.</p>
                """,
                tag="Best Practices",
            ),
            BlogPost(
                title="Climate-smart agriculture: adapting to a warming world",
                slug="climate-smart-agriculture",
                summary="How farmers can adapt planting strategies, crop selection, and water management to a changing climate.",
                body="""
                <p>Global temperatures are rising, rainfall patterns are shifting, and extreme weather events
                are becoming more frequent. Agriculture — which feeds 8 billion people — must adapt.</p>

                <h2>Shifting planting windows</h2>
                <p>In many regions, the optimal planting date has moved by 1–3 weeks over the past two decades.
                AI models that combine historical weather data with seasonal forecasts can help farmers
                pinpoint the best sowing time for their specific location.</p>

                <h2>Drought-tolerant varieties</h2>
                <p>Plant breeders have developed crop varieties that use 20–30% less water while maintaining
                yield. Combining these genetics with precision irrigation can dramatically reduce water waste.</p>

                <h2>Cover cropping and mulching</h2>
                <p>Keeping the soil covered between cash crop seasons reduces erosion, retains moisture,
                and builds organic matter. Cover crops like clover and rye also fix nitrogen, reducing
                fertiliser costs in the following season.</p>
                """,
                tag="Climate",
            ),
            BlogPost(
                title="Precision irrigation: every drop counts",
                slug="precision-irrigation",
                summary="Sensor-driven drip irrigation can cut water usage by 40% while boosting yields.",
                body="""
                <p>Water scarcity is the defining agricultural challenge of the 21st century. Precision
                irrigation — using sensors, weather data, and automation — ensures that every drop of water
                reaches the root zone exactly when the plant needs it.</p>

                <h2>How it works</h2>
                <p>Soil moisture sensors buried at multiple depths transmit data to a controller. The
                controller cross-references this with evapotranspiration forecasts and activates drip
                lines only when the soil moisture drops below a crop-specific threshold.</p>

                <h2>The economic case</h2>
                <p>A study in Maharashtra, India, found that sensor-driven drip systems reduced water
                consumption by 42% compared to flood irrigation, while increasing tomato yields by 18%.
                The system paid for itself within two growing seasons.</p>

                <h2>Integration with AgriSense</h2>
                <p>By logging your soil readings in the AgriSense dashboard, you build a historical
                dataset that can inform irrigation scheduling. Over time, the AI learns your field's
                unique water-holding characteristics.</p>
                """,
                tag="Best Practices",
            ),
        ]
        db.session.add_all(demo)
        db.session.commit()


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)