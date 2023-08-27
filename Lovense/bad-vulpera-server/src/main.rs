use cumulus::cinfoln;
use mongodb::{bson::Document, Database};
use rand::Rng;
use warp::Filter;

#[derive(serde::Deserialize, Debug)]
struct RequestQrCode {
    name: String,
    secret: String,
}

#[derive(serde::Deserialize, serde::Serialize, Debug)]
struct LovenseQrCodeRequest {
    token: String,
    uid: String,
    uname: String,
    utoken: String,
}

#[derive(serde::Deserialize, serde::Serialize, Debug)]
struct LovenseQrCodeResponse {
    code: i32,
    message: String,
    result: bool,
    data: Option<LovenseQrCodeResponseData>,
}

#[derive(serde::Deserialize, serde::Serialize, Debug)]
struct LovenseQrCodeResponseData {
    qr: String,
    code: String,
}

#[derive(serde::Deserialize, serde::Serialize, Debug)]
struct DataDocument {
    secret: String,
}

const LOVENSE_URL: &str = "https://api.lovense-api.com/api/lan";

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    connect_db().await?;

    let request_qr_code = warp::path!("requestQrCode")
        .and(warp::post())
        .and(warp::body::json())
        .and_then(|body: RequestQrCode| async move {
            let http_client = reqwest::Client::new();

            let mut headers = reqwest::header::HeaderMap::new();

            headers.insert(
                reqwest::header::CONTENT_TYPE,
                reqwest::header::HeaderValue::from_static("application/json"),
            );
            headers.insert(
                reqwest::header::USER_AGENT,
                reqwest::header::HeaderValue::from_static("Bad-Vulpera-Server"),
            );

            let mongodb_uri = std::env::var("MONGODB_URI").unwrap();

            let mongo_client = mongodb::Client::with_uri_str(&mongodb_uri).await.unwrap();
            let db = mongo_client.database("bad-vulpera-lovense");
            let collection: mongodb::Collection<DataDocument> = db.collection("data");
            let result = collection.find_one(None, None).await.unwrap();

            if result.is_some() {
                let data = result.unwrap();

                // Check if data.secret has a $ in it
                if data.secret.contains("$") {
                    // Hash the secret

                    // Get the salt
                    let salt_string = data.secret.split("$").collect::<Vec<&str>>()[1];
                    let salt = hex::decode(salt_string).unwrap();

                    // Hash the secret with the salt
                    let mut hasher = blake3::Hasher::new();

                    hasher.update(body.secret.as_bytes());
                    hasher.update(&salt);

                    let hash = hasher.finalize();

                    let hash_string = hex::encode(hash.as_bytes());

                    // Check if the hash matches
                    if hash_string == data.secret.split("$").collect::<Vec<&str>>()[2] {
                        // Hash matches, send the request to Lovense

                        let utoken = rand::thread_rng()
                            .sample_iter(&rand::distributions::Alphanumeric)
                            .take(32)
                            .map(char::from)
                            .collect::<String>();

                        let uid = rand::thread_rng()
                            .sample_iter(&rand::distributions::Alphanumeric)
                            .take(32)
                            .map(char::from)
                            .collect::<String>();

                        let token = std::env::var("LOVENSE_TOKEN").unwrap();

                        let req_data = LovenseQrCodeRequest {
                            token,
                            uid,
                            uname: body.name,
                            utoken,
                        };

                        let res = http_client
                            .post(LOVENSE_URL.to_string() + "/getQrCode")
                            .headers(headers)
                            .json(&req_data)
                            .send()
                            .await
                            .unwrap();

                        let res_json = res.json::<LovenseQrCodeResponse>().await.unwrap();

                        cinfoln!("{:?}", res_json);

                        let message = res_json.message;

                        // Return the response
                        return Ok::<_, warp::Rejection>(warp::reply::with_status(
                            message,
                            warp::http::StatusCode::OK,
                        ));
                    } else {
                        // Hash doesn't match, return an error
                        return Ok::<_, warp::Rejection>(warp::reply::with_status(
                            "Invalid secret".to_string(),
                            warp::http::StatusCode::UNAUTHORIZED,
                        ));
                    }
                }
            }

            Ok::<_, warp::Rejection>(warp::reply::with_status(
                "OK".to_string(),
                warp::http::StatusCode::OK,
            ))
        });

    let routes = request_qr_code;

    warp::serve(routes).run(([0, 0, 0, 0], 3030)).await;

    Ok(())
}

async fn connect_db() -> Result<(), Box<dyn std::error::Error>> {
    let mongodb_uri = std::env::var("MONGODB_URI")?;

    let client = mongodb::Client::with_uri_str(&mongodb_uri).await?;
    let db = client.database("bad-vulpera-lovense");
    let collection: mongodb::Collection<DataDocument> = db.collection("data");
    let result = collection.find_one(None, None).await?;

    if result.is_some() {
        let data = result.unwrap();

        // Check if data.secret has a $ in it
        if !data.secret.contains("$") {
            // Hash the secret

            // Generate a random salt
            let salt = rand::thread_rng().gen::<[u8; 16]>(); // 128 bits

            // Hash the secret with the salt
            let mut hasher = blake3::Hasher::new();

            hasher.update(data.secret.as_bytes());
            hasher.update(&salt);

            let hash = hasher.finalize();

            let hash_string = hex::encode(hash.as_bytes());
            let salt_string = hex::encode(salt);

            // Update the secret
            collection
                .update_one(
                    mongodb::bson::doc! {
                        "secret": &data.secret
                    },
                    mongodb::bson::doc! {
                        "$set": {
                            "secret": format!("${}${}", salt_string, hash_string)
                        }
                    },
                    None,
                )
                .await?;

            cinfoln!("Updated secret to {}", &data.secret);
        }
    }

    Ok(())
}
