document.addEventListener('DOMContentLoaded', function () {
    initiateCategoryFlow()
    initLocationFlow()
})

function initiateCategoryFlow() {
    // load main category
    loadChildren('/ads/ajax/categories/0/', callback = (data) => {
        addDropdown(
            sectionId = 'category_section',
            level = 1,
            labelText = "Category: " + level,
            options = data.items,
            onChange = handleCategoryChange
        )
    })
}

function handleCategoryChange(categoryId, level) {
    removeChildDropdowns(sectionId, level + 1);
    document.getElementById("id_category").value = "";

    if (!categoryId) return

    loadChildren(`/ads/ajax/categories/${categoryId}/`, data => {
        if (data.items.length) {
            addDropdown(
                sectionId = "category_section",
                level = level + 1,
                labelText = "Category: " + level,
                items = data.items,
                onChange = handleCategoryChange
            )
        } else {
            document.getElementById("id_category").value = categoryId
        }
    })
}

function initLocationFlow() {
    loadChildren("/ads/ajax/locations/", data => {
        addDropdown(
            sectionId = "location_section",
            level = 1,
            labelText = "Location",
            items = data.items,
            onChange = handleLocationChange
        );
    });
}

function handleLocationChange(locationId, level) {
    clearNeighbourhood(level)
    if (!locationId) return;

    loadChildren(`/ads/ajax/cities/${locationId}/`, data => {
        addDropdown(
            sectionId = "location_section",
            level = level + 1,
            labelText = "City",
            items = data.items,
            onChange = handleCityChange
        );
    });
}

function handleCityChange(cityId, level) {
    clearNeighbourhood(level)
    if (!cityId) return;

    loadChildren(`/ads/ajax/neighbourhoods/${cityId}/`, data => {
        if (data.items.length) {
            addDropdown(
                sectionId = "location_section",
                level = level + 1,
                labelText = "Neighbourhood",
                items = data.items,
                onChange = handleNeighbourhoodChange
            );
        }
    });
}

function handleNeighbourhoodChange(neighbourhoodId) {
    document.getElementById("id_neighbourhood").value = neighbourhoodId;
}

function clearNeighbourhood(level) {
    const sectionId = "location_section";

    removeChildDropdowns(sectionId, level + 1);
    document.getElementById("id_neighbourhood").value = "";
}

function loadChildren(url, callback) {
    fetch(url).then(response => response.json()).then(callback)
}

function addDropdown(sectionId, level, labelText, options, onChange) {
    const section = document.getElementById(sectionId)
    removeChildDropdowns(sectionId, level)

    const paragraph = document.createElement("p")
    const label = document.createElement("label")
    label.textContent = labelText
    paragraph.dataset.level = level
    paragraph.appendChild(label)

    const selectList = document.createElement("select")
    selectList.classList.add('form-control')

    selectList.appendChild(prepareCategoryOption("", "---------"))
    options.forEach(category => {
        selectList.appendChild(prepareCategoryOption(category.id, category.name))
    })

    selectList.onchange = e => onChange(e.target.value, level);

    paragraph.appendChild(selectList)
    section.appendChild(paragraph)
}

function prepareCategoryOption(value, text) {
    let option = document.createElement("option")
    option.value = value
    option.text = text
    return option
}

function removeChildDropdowns(sectionId, fromLevel) {
    console.log(sectionId)
    const section = document.getElementById(sectionId)
    const paragraphs = section.querySelectorAll('p')

    paragraphs.forEach(p => {
        const level = parseInt(p.dataset.level, 10)

        if (!isNaN(level) && level >= fromLevel) {
            p.remove()
        }
    })
}
