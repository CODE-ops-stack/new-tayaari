import org.apache.pdfbox.pdmodel.PDDocument
import org.apache.pdfbox.text.PDFTextStripper
import java.io.File

fun main() {
    val file = File("../../source-material/question.pdf")
    if (!file.exists()) {
        println("File not found")
        return
    }
    PDDocument.load(file).use { document ->
        val stripper = PDFTextStripper()
        val text = stripper.getText(document)
        File("extracted.txt").writeText(text)
        println("Extracted to extracted.txt")
    }
}
