document.addEventListener('DOMContentLoaded', function () {
    initiateCategoryFlow()
    initLocationFlow()
    // pre-loaded data (category and location hierarchy)
    window.pageContext = JSON.parse(document.getElementById('page-context').textContent);
})

function initiateCategoryFlow() {
    // load main category
    handleCategoryChange(sectionId = 'category_section', categoryId = 0, level = 0)
}

function handleCategoryChange(sectionId, categoryId = null, level) {
    removeChildDropdowns(sectionId, level + 1);
    document.getElementById('id_category').value = '';
    document.getElementById('property-container').innerHTML = ''

    if (categoryId === null) return

    loadChildren(`/ads/ajax/category_children/${categoryId}/`, data => {
        if (data.items.length) {
            let selectElement = addDropdown(
                sectionId = sectionId,
                level = level + 1,
                labelText = 'Category: ' + level,
                items = data.items,
                onChange = handleCategoryChange
            )
            if (pageContext && pageContext.category_hierarchy) {
                selectOptionFromArray(selectElement, pageContext.category_hierarchy.map(category => category.id));
            }
        } else {
            document.getElementById('id_category').value = categoryId
            if (categoryId) {
                let adId = document.getElementById('id_ad').dataset.adId;
                console.log(adId)
                console.log(categoryId)
                loadChildren(url = `/ads/ajax/load-category-properties/?category_id=${categoryId}&ad_id=${adId}`, data => {
                    document.getElementById('property-container').innerHTML = data.html;
                })
            }
        }
    })
}

function initLocationFlow() {
    loadChildren('/ads/ajax/locations/', data => {
        let selectElement = addDropdown(
            sectionId = 'location_section',
            level = 1,
            labelText = 'Location',
            items = data.items,
            onChange = handleLocationChange
        );
        if (pageContext.location_hierarchy && pageContext.location_hierarchy.location) {
            selectOptionFromArray(selectElement, [pageContext.location_hierarchy.location.id]);
        }
    });
}

function handleLocationChange(sectionId, locationId, level) {
    clearNeighbourhood(level)
    if (!locationId) return;

    loadChildren(`/ads/ajax/cities/${locationId}/`, data => {
        let selectElement = addDropdown(
            sectionId = sectionId,
            level = level + 1,
            labelText = 'City',
            items = data.items,
            onChange = handleCityChange
        );
        if (pageContext.location_hierarchy && pageContext.location_hierarchy.city) {
            selectOptionFromArray(selectElement, [pageContext.location_hierarchy.city.id]);
        }
    });
}

function handleCityChange(sectionId, cityId, level) {
    clearNeighbourhood(level)
    if (!cityId) return;

    loadChildren(`/ads/ajax/neighbourhoods/${cityId}/`, data => {
        if (data.items.length) {
            let selectElement = addDropdown(
                sectionId = sectionId,
                level = level + 1,
                labelText = 'Neighbourhood',
                items = data.items,
                onChange = handleNeighbourhoodChange
            );
            console.log('neighbourhood')
            if (pageContext.location_hierarchy && pageContext.location_hierarchy.neighbourhood) {
                selectOptionFromArray(selectElement, [pageContext.location_hierarchy.neighbourhood.id]);
            }
        }
    });
}

function handleNeighbourhoodChange(sectionId, neighbourhoodId) {
    document.getElementById('id_neighbourhood').value = neighbourhoodId;
}

function clearNeighbourhood(level) {
    const sectionId = 'location_section';

    removeChildDropdowns(sectionId, level + 1);
    document.getElementById('id_neighbourhood').value = '';
}

function loadChildren(url, callback) {
    fetch(url).then(response => response.json()).then(callback)
}

function addDropdown(sectionId, level, labelText, options, onChange) {
    const section = document.getElementById(sectionId)
    removeChildDropdowns(sectionId, level)

    const paragraph = document.createElement('p')
    const label = document.createElement('label')
    label.textContent = labelText
    paragraph.dataset.level = level
    paragraph.appendChild(label)

    const selectElement = document.createElement('select')
    selectElement.classList.add('form-control')

    selectElement.appendChild(prepareOption('', '---------'))
    options.forEach(category => {
        selectElement.appendChild(prepareOption(category.id, category.name))
    })

    selectElement.onchange = e => onChange(sectionId, e.target.value, level);
    paragraph.appendChild(selectElement)
    section.appendChild(paragraph)
    return selectElement
}

function prepareOption(value, text) {
    let option = document.createElement('option')
    option.value = value
    option.text = text
    return option
}

function removeChildDropdowns(sectionId, fromLevel) {
    const section = document.getElementById(sectionId)
    const paragraphs = section.querySelectorAll('p')

    paragraphs.forEach(p => {
        const level = parseInt(p.dataset.level, 10)

        if (!isNaN(level) && level >= fromLevel) {
            p.remove()
        }
    })
}

function selectOptionFromArray(selectElement, targetArray) {
    let valueToSelect = '0'; // Default value
    for (const value of targetArray) {
        const optionExists = selectElement.querySelector(`option[value='${value}']`) !== null;
        if (optionExists) {
            valueToSelect = value;
            break;
        }
    }
    selectElement.value = valueToSelect;
    selectElement.dispatchEvent(new Event('change'));
}
