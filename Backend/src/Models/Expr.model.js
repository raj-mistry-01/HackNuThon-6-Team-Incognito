import mongoose from "mongoose";

const exprSchema = new mongoose.Schema({
    text: { type: String, required: true }
});

const Expr = mongoose.model("Expr", exprSchema);

export default Expr;
