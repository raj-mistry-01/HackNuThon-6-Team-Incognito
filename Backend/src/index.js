import connectToMongo from "./db/db.js";
import dotenv from "dotenv";
import {app} from "./app.js"
dotenv.config();
connectToMongo()
const port = 7000
const server = app.listen(port, () => {
    console.log(`App listening at http://localhost:${port}`);
});