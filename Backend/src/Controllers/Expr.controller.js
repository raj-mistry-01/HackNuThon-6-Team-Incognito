import Expr from "../Models/Expr.model.js";

const sendexpr = async (req, res) => {
    try {
        console.log("yes");
        const { text } = req.body;
        if (!text) return res.status(400).json({ error: "Text is required" });

        const newExpr = new Expr({ text });
        await newExpr.save();

        res.status(201).json({ message: "Inserted successfully", data: newExpr });
    } catch (error) {
        res.status(500).json({ error: "Server Error", details: error.message });
    }
};

// Use named export instead of default
export { sendexpr };
