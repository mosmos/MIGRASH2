from datetime import datetime
import os

gdbpath="C:\DEV\GDATA"
datapath="C:\\DEV\\GDATA"
connectionpath="C:\DEV\connectionfile\\dgt-sde01db720.sde\\"
excelpath="C:\DEV\MIGRASH2\MIGRASH_MILON.xlsx"
username = os.getlogin()

TopHTML = """
<!DOCTYPE html>
<html>
<html dir="rtl" lang="ar"></html>
<head>
  <style>
    body {
      font-family: 'Calibri', sans-serif;
    }
  </style>
</head>
<body>
"""
TopHTMLwithfilter = """
<!DOCTYPE html>
<html>
<html dir="rtl" lang="ar"></html>
<head>
  <style>
    body {
      font-family: 'Calibri', sans-serif;
    }
  </style>
  <title>כרטיס מגרש ציבורי</title>
  <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
  <script>
    $(document).ready(function() {
      // populate the drop-down list with the ids of the sections
      $("div[id^='מגרש-']").each(function() {
        $("#filter").append("<option value='" + this.id + "'>" + this.id + "</option>");
      });

      // hide all sections except the one selected from the drop-down list
      $("#filter").change(function() {
        var selected = $(this).val();
        $("div[id^='מגרש-']").hide();
        if (selected) {
          $("#" + selected).show();
        } else {
          $("div[id^='מגרש-']").show();
        }
      });
    });
  </script>
<body>
  <select id="filter" class="sticky-filter" style="position: fixed; top: 0%; right: 30%; z-index: 999; width: 10%; background-color: gray; padding: 0.5em 1em; font-size: 1em; font-weight: bold;text-align: center;">
    <option value="">הצג הכל</option>
  </select>
"""

TopHTMLurlfilter = """
<!DOCTYPE html>
<html>
<html dir="rtl" lang="ar"></html>
<head>
  <style>
    body {
      font-family: 'Calibri', sans-serif;
    }
  </style>
  <title>כרטיס מגרש ציבורי</title>
    <script>
      function getUrlParameter(name) {
        name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
        var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
        var results = regex.exec(location.search);
        return results === null
          ? ''
          : decodeURIComponent(results[1].replace(/\+/g, ' '));
      }
      window.onload = function() {
        var sectionId = getUrlParameter('section');
        if (sectionId) {
          var sections = document.getElementsByClassName('section');
          for (var i = 0; i < sections.length; i++) {
            if (sections[i].id === sectionId) {
              sections[i].style.display = 'block';
            } else {
              sections[i].style.display = 'none';
            }
          }
        }
      };
    </script>
  </head>
  <body>
"""

