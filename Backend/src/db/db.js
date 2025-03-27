import mongoose from "mongoose";
import dotenv from "dotenv";

const connectToMongo = async () => {
    // dotenv.config({ path: "..\.env" });
    dotenv.config({ path: "../../.env" });
  try {
    console.log(process.env.MONGO_URI);
    await mongoose.connect(process.env.MONGO_URI);
    console.log("Connected to MongoDB");
  } catch (error) {
    console.error("Error connecting to MongoDB:", error);
    process.exit(1);
  }
};
connectToMongo()

export default connectToMongo;
