from selenium import webdriver
from selenium.webdriver.common.by import By

def get_full_xpath(driver, element):
    return driver.execute_script("""
    function getAbsoluteXPath(element) {
        var path = [];
        while (element && element.nodeType === Node.ELEMENT_NODE) {
            var index = 0;
            var sibling = element.previousSibling;
            while (sibling) {
                if (sibling.nodeType === Node.ELEMENT_NODE && sibling.nodeName === element.nodeName) {
                    index++;
                }
                sibling = sibling.previousSibling;
            }
            var tagName = element.nodeName.toLowerCase();
            var pathIndex = index ? "[" + (index + 1) + "]" : "";
            path.unshift(tagName + pathIndex);
            element = element.parentNode;
        }
        return "/" + path.join("/");
    }
    return getAbsoluteXPath(arguments[0]);
    """, element)

def get_interactive_elements(driver):
    interactive_xpaths = [
        "//input[@type='text']",
        "//input[@type='password']",
        "//input[@type='email']",
        "//input[@type='number']",
        "//input[@type='checkbox']",
        "//input[@type='radio']",
        "//textarea",
        "//select",
        "//button",
        "//div[contains(@contenteditable, 'true')]",
        "//span[contains(@contenteditable, 'true')]",
        "//div[contains(@role, 'button')]",
        "//div[contains(@role, 'checkbox')]",
        "//div[contains(@role, 'radio')]",
        "//div[contains(@role, 'textbox')]",
        "//div[contains(@role, 'combobox')]"
    ]
    
    elements = []
    for xpath in interactive_xpaths:
        found_elements = driver.find_elements(By.XPATH, xpath)
        for element in found_elements:
            xpath_full = get_full_xpath(driver, element)
            elements.append((element, xpath_full))
    
    return elements

def main():
    driver = webdriver.Edge()
    driver.get('http://docs.google.com/forms/d/1UZkASiSkVhUnS-ppKGi7mStAF14UAw5zL_YIvHMzIjM/')
    
    interactive_elements = get_interactive_elements(driver)
    
    for element, xpath in interactive_elements:
        print(f"XPath Completa: {xpath}")
        print(f"Outer HTML: {driver.execute_script('return arguments[0].outerHTML;', element)}\n")
        print('-----')
    
    driver.quit()

if __name__ == "__main__":
    main()


'''
from selenium import webdriver
from selenium.webdriver.common.by import By

# Initialize WebDriver (adjust path to your driver if necessary)
driver = webdriver.Firefox()

# Open the desired website
#driver.get("https://practice-automation.com/form-fields/")
driver.get("http://docs.google.com/forms/d/1UZkASiSkVhUnS-ppKGi7mStAF14UAw5zL_YIvHMzIjM/")
#driver.get("https://forms.gle/CF9sM8k9hrb6KAzJA")

# Find all writable input fields and text areas
writable_elements = driver.find_elements(By.XPATH, "//input[@type='text' or @type='email' or @type='password' or @type='number' or @type='url' or @type='tel' or @type='search'] | //textarea")
#writable_elements = driver.find_elements(By.XPATH, "//input | //textarea | //div | //span")
#writable_elements = driver.find_elements(By.XPATH, "//html")
# Print out the XPath for each writable element
for element in writable_elements:
    xpath = element.get_attribute("xpath")
    if not xpath:
        # Generate XPath if not predefined
        xpath = driver.execute_script(
            """function absoluteXPath(element) {
                 var comp, comps = [];
                 var parent = null;
                 var xpath = '';
                 var getPos = function(element) {
                   var position = 1, curNode;
                   if (element.nodeType == Node.ATTRIBUTE_NODE) {
                     return null;
                   }
                   for (curNode = element.previousSibling; curNode; curNode = curNode.previousSibling){
                     if (curNode.nodeName == element.nodeName){
                       ++position;
                     }
                   }
                   return position;
                 };
                 for (; element && element.nodeType == Node.ELEMENT_NODE; element = element.parentNode) {
                   comp = comps[comps.length] = {};
                   comp.name = element.nodeName.toLowerCase();
                   comp.position = getPos(element);
                 }
                 for (var i = comps.length - 1; i >= 0; i--) {
                   comp = comps[i];
                   xpath += '/' + comp.name;
                   if (comp.position != null && comp.position != 1) {
                     xpath += '[' + comp.position + ']';
                   }
                 }
                 return xpath;
               }
               return absoluteXPath(arguments[0]);""",
            element
        )
    print(xpath)

# Close the WebDriver
driver.quit()
'''