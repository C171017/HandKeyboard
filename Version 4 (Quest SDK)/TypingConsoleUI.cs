using TMPro;
using UnityEngine;

public class TypingConsoleUI : MonoBehaviour
{
    public TextMeshProUGUI outputText;
    private string currentText = "";

    public void Append(char input)
    {
        currentText += input;
        outputText.text = currentText;
    }

    public void ClearText()
    {
        currentText = "";
        outputText.text = "";
    }
}
